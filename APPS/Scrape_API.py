from Result import Result
import APPS.MDLottery3 as MDLottery
import APPS.WVLottery3 as WVLottery
from helper import *

class Scrape:
    """ A class to manage which scrape scripts to run.
    """

    def __init__(self) -> None:
        """ Initialize a new Class instance."""
        return
    
    def parse_command(self, entities:dict) -> list['Result']:
        """Parse Natural Language entities and execute corresponding 
        scraping script
        Args:
            entities (tuple):   Collection of names entities extracted from 
                                user input, where each entitiy has a label
        
        Expected Entitiy Labels:
            - TYPE: Which script to run

        Returns:
            Result: Result object indicating success/failure and containing 
                    relevant data or error messages.
        """

        options = ["mdlottery", "wvlottery"]
        type_entities = entities.get("TYPE", [])

        if not type_entities:
            return [Result(False, "No type specified", entities)]

        completed_scrapes = []
        for ent in type_entities:
            scrape_type = ent.get("text", "").lower()

            match scrape_type:
                case "mdlottery":
                    completed_scrapes.append(MDLottery.main())
                case "wvlottery":
                    completed_scrapes.append(WVLottery.main())
                case _:
                    completed_scrapes.append(
                        Result(False, f"Unsupported lottery type: '{scrape_type}'")
                    )
                    log("Results", f"WARNING: Unsupported scrape type: '{scrape_type}'")

        if not completed_scrapes:
            return [Result(False, "Nop supported lotteries found in request", entities)]
        
        return completed_scrapes