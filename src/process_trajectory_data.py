import pandas as pd
import numpy as np
import json

def save_trajectory_data_one_rally(one_point_sequence):
    '''
    Args:
    -----
    one_point_sequence [dict]: Dictionary
    
    Returns:
    --------
    pandas DataFrame (for one point sequence)
    
    Notes:
    ------
    '''
    
    ball_trajectory_df = pd.DataFrame(one_point_sequence['trajectoryData'])
    
    if ball_trajectory_df.empty:
        return ball_trajectory_df
    
    #######################################################################
    #                     Match situation information                     #
    #######################################################################
    # --> Get indices where ball is hit 
    hit_indices = ball_trajectory_df.index[ball_trajectory_df['position'] == 'hit'].tolist()
    hit_indices.append(ball_trajectory_df.shape[0])

    # Get lengths of rally index (expect 4 or 5)
    # In the usual case, we expect this sequence: Hit --> Peak --> Net --> Bounce
    # But what if it's a half volley? (Hit --> Peak --> Net)
    # But what if it's a hit on the rise?  Hit --> Peak --> Net --> Bounce --> Peak
    # *** Ball trajectory also includes erroneous balls (mishits)...so we sometimes get strike_index = 1 + rally_index
    hit_indices_diff_len = [x - hit_indices[i - 1] for i, x in enumerate(hit_indices)][1:]

    rally_length = len(hit_indices_diff_len)

    rally_index_list = []
    for rally_ind in range(1, rally_length + 1):
        rally_index_list.append(np.repeat( rally_ind, repeats=hit_indices_diff_len[rally_ind-1]))
    
    # Combine a list of numpy arrays into a single array
    try: 
        ball_trajectory_df['strike_index'] = np.concatenate( rally_index_list, axis=0 )
        
    except ValueError:
        # -- Added because one instance of a rally having only a single 'bounce' obs. and nothing else!
        ball_trajectory_df['strike_index'] = [None]*ball_trajectory_df.shape[0]
    
    ##################################################
    #          Match situation information           #
    ##################################################
    ball_trajectory_df['point_ID'] = one_point_sequence['pointId']
    ball_trajectory_df['set_num'] = one_point_sequence['set']
    ball_trajectory_df['game_num'] = one_point_sequence['game'] 
    ball_trajectory_df['point_num'] = one_point_sequence['point']
    ball_trajectory_df['serve_num'] = one_point_sequence['serve']
    
    return ball_trajectory_df



def get_match_point_ball_trajectory_data(raw_json_file):
    '''
    Args:
    -----
    one_point_sequence [dict]: Dictionary
    
    Returns:
    --------
    pandas DataFrame
    '''
    all_tracking_data_dict = raw_json_file['courtVisionData'][0]['pointsData']
    
    match_ball_trajectory_list = []
    
    for point_id_key in sorted(all_tracking_data_dict.keys()):
        #print(point_id_key)
        ball_trajectory_df = save_trajectory_data_one_rally( all_tracking_data_dict[point_id_key] )
        
        if ball_trajectory_df.empty:
            continue
        else:
            match_ball_trajectory_list.append( ball_trajectory_df )

    try:        
        match_ball_trajectory_df = pd.concat(match_ball_trajectory_list)
    
    
        ### Reorder columns
        match_ball_trajectory_df = match_ball_trajectory_df[['point_ID', 'set_num', 'game_num', 'point_num', 'serve_num', 'strike_index', 'position', 'x', 'y', 'z' ]]
        match_ball_trajectory_df[['set_num', 'game_num', 'point_num', 'serve_num']] = match_ball_trajectory_df [['set_num', 'game_num', 'point_num', 'serve_num']].astype(int)
        match_ball_trajectory_df .sort_values(by = ['set_num', 'game_num', 'point_num', 'serve_num'], inplace = True)
                    
    except ValueError:
        match_ball_trajectory_df = pd.DataFrame(match_ball_trajectory_list)
        
        
    
    
    return match_ball_trajectory_df#.reset_index(inplace = True)

    