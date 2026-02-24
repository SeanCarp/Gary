import pickle, os, re
import Result

class Grade_Checker:
    """ A class to manage and track grades across multiple classes.
    NOTE: The logic behind making sure all the sections are added in must be 
    done by the user. Currently, no intentions to change this.
    """
    
    def __init__(self) -> None:
        """ Initialize a new Grade_Checker instance.
        Creates an empty list to store Class objects.
        """
        self.filename = "Gary_log/school_grades.pkl"
        self.classes = []
        self.class_grades = []

        self.load_data()

    def add_class(self, class_name:str) -> 'Result':
        """ Add a new class to the grade checker.
        Args:
            class_name (str): The name of the class to add.
        """
        try:
            if class_name in [cls.class_name for cls in self.classes]:
                return Result(False, f"Class, '{class_name}', was already created, please enter new class")
            self.classes.append(self.Class(class_name))
            self.save_data()
            return Result(True, f"{class_name} added successfully")
        except Exception as e:
            return Result(False, f"{e}: Error adding class")
        
    def remove_class(self, class_name:str) -> 'Result':
        """ Removes a class from the grade checker.
        Args:
            class_name (str): The name of the class to remove.
        """
        try:
            found_class = self.find_class(class_name)
            if found_class is None:
                return Result(False, f"Class '{class_name}' not found. Cannot remove non-existent class.")
            
            self.classes = [cls for cls in self.classes if cls.class_name != class_name]
            self.class_grades = [grade for grade in self.class_grades if not grade.startswith(f"{class_name}")]

            self.save_data()
            return Result(True, f"Class '{class_name}' removed successfully")
        except Exception as e:
            return Result(False, f"Error removing class '{class_name}': {e}")


    def add_section(self, class_name:str, section_name:str, section_points:float) -> 'Result':
        """ Add a section (assignment/exam) to a specific class.
        Args:
            class_name (str):   The name of the class to add the section to.
            section_name (str):         The name of the section to add.
            section_points (float):     The point value for the section.                   
        """
        found_class = self.find_class(class_name)
        if found_class is not None:
            temp = found_class.add_section(section_name, section_points)
            self.save_data()
            return temp
        else:
            return Result(False, f"Class, {class_name}, not found. Please add the class first. (add_section)")

    def remove_section(self, class_name:str, section_name:str) -> 'Result':
        """ Removes a section (assignment/exam) to a specific class.
        Args:
            class_name (str):       The name of the class to a remove section to.
            section_name (str):     The name of the section to be removed.
        """
        found_class = self.find_class(class_name)
        if found_class != None:
            temp = found_class.remove_section(section_name)
            self.save_data()
            return temp
        else:
            return Result(False, f"Class, {class_name}, not found. Please add the class first. (remove_section)")

    def add_grade(self, class_name:str, section_name:str, points:int, max_points:int) -> 'Result':
        """ Adds grade to given class and given section.
        Args:
            class_name (str):       The name of the class to a remove section to.
            section_name (str):     The name of the section to be removed.
            points (int):           Points earned on the assignment.
            max_points (int):       Maximum possible points for the assignment.
        """
        found_class = self.find_class(class_name)
        if found_class != None:
            temp = found_class.add_grade(section_name, points, max_points)
            self.save_data()
            return temp
        else:
            return Result(f"Class, {class_name}, not found. Please add the class first. (add_grade)")

    def remove_grade(self, class_name:str, section_name:str, points:int, max_points:int) -> 'Result':
        """ Removes grade from given class and given section.
        Args:
            class_name (str):       The name of the class to a remove section to.
            section_name (str):     The name of the section to be removed.
            points (int):           Points earned on the assignment.
            max_points (int):       Maximum possible points for the assignment.
        """
        found_class = self.find_class(class_name)
        if found_class != None:
            temp = found_class.remove_grade(section_name, points, max_points)
            self.save_data()
            return temp
        else:
            return Result(False, f"Class, {class_name}, not found. Please add the class first. (remove_grade)")

    def check_grade(self, class_name:str, blowout:bool=False) -> 'Result':
        """ Calculates and shows the grade of given class name.
        Args:
            class_name (str):           The name of the class to a remove section to.
            blowout (bool, optional):   If True, prints deatiled grade info for each section.
        Returns:
            GradeResult: A result object containing:
                - success (bool):   True if grade was successfully removed, False otherwise
                - message (str):    Description of the operation result
                - data (any):       None for this operation
        """
        found_class = self.find_class(class_name)
        if found_class != None:
            temp = found_class.check_grade(blowout)
            self.save_data
            return temp
        else:
            return Result(False, f"Class, {class_name}, not found. Please add the class first. (check_grade)")

    def check_grades(self) -> 'Result':
        """ Calculate and shows all of the grades.
        Returns:
            GradeResult: A result object containing:
                - success (bool):   True if grade was successfully removed, False otherwise
                - message (str):    Description of the operation result
                - data (any):       None for this operation
        """
        if self.classes is None:
            return Result(False, "No classes found. Please create class first before check grades")
        
        for cls in self.classes:
            self.class_grades.append((cls.check_grade(False).to_dict().get('message')))
        self.save_data()
        return Result(True, "", self.class_grades) # ["MAE342: 98.3"]
    
    def find_class(self, class_name:str) -> 'Grade_Checker.Class | None':
        """ Find a class by name.
        Args:
            class_name (str): The name of the class to find.

        Returns:
            Grade_Checker.Class | None: The class object if found, None otherwise.
        """
        for cls in self.classes:
            if cls.class_name == class_name:
                return cls
        return None
    
    def save_data(self, filename:str=None) -> None:
        """ Save the Grade_Checker data to a pickle file.
        Args:
            filename (str, optional): Override the default filename
        """
        save_file = filename or self.filename
        try:
            directory = os.path.dirname(save_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            save_data = {
                'classes': self.classes,
                'class_grades': self.class_grades,
                'filename': save_file
            }

            with open(save_file, 'wb') as f:
                pickle.dump(save_data, f)
            return print(f"Data saved successfully to {save_file}")
        except Exception as e:
            return print(f"Error saving data: {e}")
        
    def load_data(self, filename:str=None) -> None:
        """ Load Grade_Checker data from a pickle file.
        Args:
            filename (str, optional): Override the defailt filename
        """
        load_file = filename or self.filename
        try:
            if not os.path.exists(load_file):
                return print(f"No saved data found at {load_file}")
            with open(load_file, 'rb') as f:
                loaded_data = pickle.load(f)

            if isinstance(loaded_data, dict):
                self.classes = loaded_data.get('classes', [])
                self.class_grades = loaded_data.get('class_grades',[])
                self.filename = loaded_data.get('filename')
            
            return print(f"Loaded {len(self.classes)} classes.")
        except Exception as e:
            return print(f"Error loading data: {e}")
        
    def parse_command(self, entities:dict) -> 'Result':
        """Parse Natural Language entities and execute corresponding grade checker
        Args:
            doodle_hopper (Grade_Checker):  The grade checker instance to perform operations
            entities (tuple):   Collection of named entities extracted from user input, 
                                where each entity has a label

        Expected Entity Labels:
            - ACTION: The operation to perform (add/create/make/tracking, remove/delete/drop, 
                    check/show/calculate/display)
            - CLASS: The class name to operate on
            - SECTION: The section/assignment name within a class
            - SCORE: Score information in format containing two numbers (e.g., "15/20")
            - POINTS: Point value for sections/assignments
            - BLOWOUT: Flag for detailed grade display
        
        Operation Hierarchy (most to least specific):
            1. Grade operations: Requires class_name, section, and score
            - Add/remove individual grades with scores
            2. Section operations: Requires class_name and section
            - Add sections (with points) or remove sections
            3. Class operations: Requires class_name only
            - Add/remove entire classes
            4. Check operations: Can work with or without class_name
            - Display grades for specific class or all classes
        
        Returns:
            Result: Result object indicating success/failure and containing
                        relevant data or error messages.    

        Note:
            Score format must contain exactly two numbers for grade operations.
            All action keywords are case-insensitive.
            What happens if someone enters multiple actions?
            Can this method be within the Grade_Checker API?
        """

        # MUST BE LOWERCASE
        remove_action = ["remove", "delete", "drop"]
        add_action = ["add", "create", "make", "tracking"]
        check_action = ["check", "show", "calculate", "display"]

        action = entities.get("ACTION", None)
        class_name = entities.get("CLASS", None)
        section = entities.get("SECTION", None)
        points = entities.get("POINTS", None)
        score = entities.get("SCORE", None)
        blowout = entities.get("BLOWOUT", None)

        if not action:
            return Result(False, "No action specified", entities)
        action = action.lower()


        # This is a funneling down of most specific to least
        # Grade Operations
        if class_name and section and score:
            numbers = [float(n) for n in re.findall(r'\d+', str(score))]
            if len(numbers) != 2:
                return Result(False, "Failed to add/remove grade. (Incorrect score format)", entities)
            
            if action in remove_action:
                return self.remove_grade(class_name, section, numbers[0], numbers[1])
            elif action in add_action:
                return self.add_grade(class_name, section, numbers[0], numbers[1])   

        # Section Operations
        elif class_name and section:
            if action in remove_action:
                return self.remove_section(class_name, section)
            
            elif points and action in add_action:
                return self.add_section(class_name, section, float(points))

        # Class Operations
        elif class_name:
            if action in remove_action:
                return self.remove_class(class_name)
            elif action in add_action:
                return self.add_class(class_name)
            
        # Check Grades Operations
        if action in check_action:
            if class_name:
                return self.check_grade(class_name, bool(blowout))
            return self.check_grades()
        
        return Result(False, "Invalid command combination", entities)

    class Class:
        """ A nested class representing an indiviual academic class with sections and points."""

        def __init__(self, class_name:str, sections:list[dict]=None) -> None:
            """ Initialize a new Class instance.
            Args:
                class_name (str):                   The name of the class.
                sections (list[dict], optional):    A list of section dictionaires. 
                                                    Defaults to empty list if None.
            """
            self.class_name = class_name
            self.points_sum = 0.0
            self.sections = sections or []
        
        def add_section(self, section_name:str, section_points:float) -> 'Result':
            """
            Add a section after validating the format.
            Args:
                section_name (str):         The name of the section to add.
                section_points (float):     The point value for the section.
            Returns:
                GradeResult: A result object containing:
                    - success (bool):   True if grade was successfully removed, False otherwise
                    - message (str):    Description of the operation result
                    - data (any):       None for this operation
            """
            # Validate section format
            if not isinstance(section_name, str) or not isinstance(section_points, (float, int)):
                return Result(False, "Section name must be a string and points must be a number")
            if section_points < 0:
                return Result(False, "Section points must be non-negative")
            if section_name in [section["Section"] for section in self.sections]:
                return Result(False, f"Section '{section_name}' is already added to class.")

            self.sections.append({"Section": section_name, "Points": float(section_points), "Grades": []})
            self.gen_points_sum()
            return Result(True, f"Section '{section_name}', added successfully")

        def remove_section(self, section_name:str) -> 'Result':
            """ Remove a section by its name.
            Args:
                section (str):     A string containing section
            Returns:
                GradeResult: A result object containing:
                    - success (bool):   True if grade was successfully removed, False otherwise
                    - message (str):    Description of the operation result
                    - data (any):       None for this operation
            """
            for i, section in enumerate(self.sections):
                if section["Section"] == section_name:
                    self.sections.pop(i)    # Otherwise, need full dictionary
                    self.gen_points_sum()
                    return Result(True, f'{section_name} removed successfully')
            return Result(False, f"Section '{section_name}' not found in {self.class_name} (remove_section)")

        def gen_points_sum(self) -> None:
            """ Calculate and update the total points sum for all sections.
            Iterates through all sections and sums their "Points" values,
            storing the result in self.points_sum.
            """
            points_sum = sum(item.get("Points") for item in self.sections)
            self.points_sum = points_sum

        def add_grade(self, section_name:str, points:float, max_points:float) -> 'Result':
            """ Add a grade to a specific section.
            Args:
                section_name (str):     The name of the section to add the grade to.
                points (float):           Points earned on the assignment.
                max_points (float):       Maximum possible points for the assignment.
            Returns:
                GradeResult: A result object containing:
                    - success (bool):   True if grade was successfully removed, False otherwise
                    - message (str):    Description of the operation result
                    - data (any):       None for this operation
            Notes:
                Converted to float to handle decimal points
            """
            if not isinstance(points, float) or not isinstance(max_points, float):
                return Result(False, "Points and max_points must be floats")
            if points < 0 or max_points < 0:
                return Result(False, "Max points > 0 and Points > 0")
                
            for section in self.sections:
                if section["Section"] == section_name:
                    section["Grades"].append((points, max_points))
                    return Result(True, "Grade added successfully")
            return Result(False, f"Section, '{section_name}', not found in {self.class_name}")

        def remove_grade(self, section_name:str, points: int, max_points:int) -> 'Result':
            """ Remove a grade from a specific section.
            Args:
                section_name (str):     The name of the section to add the grade to .
                points (int):           Points earned on the assignment.
                max_points (int):       Maximum possible points for the assignment.
            Returns:
                GradeResult: A result object containing:
                    - success (bool):   True if grade was successfully removed, False otherwise
                    - message (str):    Description of the operation result
                    - data (any):       None for this operation
            """
            if not isinstance(points, int) or not isinstance(max_points, int):
                return Result(False, "Points and max_points must be integers")
            if points < 0 or max_points < 0:
                return Result(False, "Max points > 0 and Points > 0")
        
            for section in self.sections:
                if section["Section"] == section_name:
                    for grade in section["Grades"]:
                        if grade[0] == points and grade[1] == max_points:
                            section["Grades"].remove(grade)
                            return Result(True, "Grade removed successfully")
                    return Result(False, f"Could not find grade {points}/{max_points} in {section}")
            return Result(f"Section '{section_name}' not found in this class")

        def check_grade(self, blowout:bool=False) -> 'Result':
            """ Calculate and optionally display the current grade for this class.
            Args:
                blowout (bool, optional):   If True, prints detailed grade info 
                                            for each section. Defaults to False.
            Returns:
                GradeResult: A result object containing:
                    - success (bool):   True if grade was successfully removed, False otherwise
                    - message (str):    Description of the operation result
                    - data (any):       None for this operation
            """
            if not self.sections:
                return Result(True, "No section found in class")
            
            class_grade = 0.0
            sections = []
            for item in self.sections:
                total_points = sum([grade[0] for grade in item["Grades"]])
                max_points = sum([grade[1] for grade in item["Grades"]])

                if max_points == 0: # Check for Divide by 0.
                    print(f"Maximum points is 0 for section, '{item['Section']}', in class, {self.class_name}. \
                          Avoiding Divide-By-0, assuming bonus points")
                    max_points = 1                    
                section_grade = item["Points"] * (total_points / max_points)
                class_grade += section_grade

                if blowout:
                    sections.append(f"{item['Section']}: ".join(f"({score[0]/{score[1]}})" for score in item["Grades"]))

            return Result(True, f"{self.class_name}: {round(class_grade,2)}", {"sections": sections})

        def __str__(self) -> str:
            return self.class_name