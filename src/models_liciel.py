from typing import Optional, List
from pydantic import BaseModel
from enum import Enum, IntEnum, StrEnum


class Missions(StrEnum):
    PLOMB = 'Plomb'
    AMIANTE_DTA = 'Amiante (DTA)'
    AMIANTE_VENTE = 'Amiante (Vente)'
    AMIANTE_DAPP = 'Amiante (DAPP)'
    METRAGE_CARREZ = 'Métrage (Loi Carrez)'
    METRAGE_BOUTIN = 'Métrage (Loi Boutin)'
    DPE = 'Diagnostique de Performance Energétique (DPE)'
    ERP = 'Etat des Risques et Pollutions (ERP)'
    ELECTRICITE = 'Electricité'
    GAZ = 'Gaz'
    TERMITES = 'Termites'

class Niveau(BaseModel):
    numero:int
    designation:str
    pass

class Piece(BaseModel):
    batiment:str
    niveau:Niveau
    numero:int
    designation:str
    visitee:bool
    
    non_visite_cause:str
    
    
class DescriptifPiece(BaseModel):
    
    
    
    # mur, sol, plafond : 
    # repérage mur a,b,c,d, ...
    # au sein d'un mur : embrasure, fenêtre, allège, chambranle, ...
    
    sol:str
    mur:str
        # a,b,c,d,e, ...
        # mur c
            # peinture sur platre
            # enduit
            # ...
            # 
    plafond:str
    fenetre:str
    

    

    
