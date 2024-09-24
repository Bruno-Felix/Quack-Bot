import pandas as pd

from utils.commands_strings import commands_idols
from utils.objekts import grid_1, grid_2, grid_3

def search_idol_on_objekts_list(objekts_list: list, idol_name: str, class_name = None, season = None, transferable = None):
    class_name = class_name if class_name else 'First'
    transferable = transferable if transferable else True
    
    objekts_list_df = pd.DataFrame(objekts_list).sort_values('collection')

    objekts_list_df.pop('backImage')
    objekts_list_df.pop('tokenId')
    objekts_list_df.pop('acquiredAt')
    objekts_list_df.pop('num')
    objekts_list_df.pop('type')

    idol_objekts_list = objekts_list_df[(objekts_list_df['memberName'] == idol_name) &
                                        (objekts_list_df['className'] == class_name) &
                                        (objekts_list_df['season'] == season) &
                                        (objekts_list_df['transferable'] == transferable)]
    
    return idol_objekts_list

def separate_idol_objekts_list_by_grids(idol_objekts_list: list):

    idol_objekts_list = pd.DataFrame(idol_objekts_list).sort_values('collection')

    idol_objekts_list_grid_1 = idol_objekts_list.query(f'collection >= {grid_1.start} and collection <= {grid_1.end}')
    idol_objekts_list_grid_2 = idol_objekts_list.query(f'collection >= {grid_2.start} and collection <= {grid_2.end}')
    idol_objekts_list_grid_3 = idol_objekts_list.query(f'collection >= {grid_3.start} and collection <= {grid_3.end}')

    return idol_objekts_list_grid_1, idol_objekts_list_grid_2, idol_objekts_list_grid_3

def separate_idol_objekts_list_by_idol(idol_objekts_list: list):
    array_idols = {}
    print('eefpfewnp')


    for idol in commands_idols:
        array_idols[idol] = idol_objekts_list[(idol_objekts_list['member'] == idol)]

    print(array_idols)

    return array_idols

def verify_if_idol_exist(idol_name = str) -> bool:
    return True if commands_idols[idol_name] else False