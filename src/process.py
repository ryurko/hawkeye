#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Functions written along the way to process Roland Garros Tracking data

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
"""

import pandas as pd
import numpy as np
import json

##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### 
##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### 
##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### 

def categorise_serve_direction(serveBounceCordinate_y):
    '''
    Args:
    -----
    serveBounceCordinate_y [int]
    
    Returns:
    --------
    Character
    
    
    Assumes Serve bounce coordinate is given in metres
    Note: (0,0,0) are the coordinates at the middle of the net.
    Dimension of court: 23.77 m in length (x), and 8.23 m wide (y) -- for single's court
    
    Classifies ball bounce coordinate as: Wide, Body, or T
    '''
    
    if serveBounceCordinate_y == None:
        return None
    
    # Court is 8.23 m wide
    one_third_length = 4.115/3

    # Tenuous at the moment
    # What if a player really miss-hits the ball, and it bounces to the opposite side of the court?
    if ( (serveBounceCordinate_y <= one_third_length) and (serveBounceCordinate_y >= -one_third_length) ):
        serve_dir = 'T'
    elif ((serveBounceCordinate_y < 2*one_third_length) and (serveBounceCordinate_y > one_third_length)  ) or ((serveBounceCordinate_y > -2*one_third_length) and (serveBounceCordinate_y < -one_third_length)  ):
        serve_dir = 'Body'
    elif (serveBounceCordinate_y >= 2*one_third_length) or ( serveBounceCordinate_y <= -2*one_third_length ):
        serve_dir = 'Wide'
    else:
        serve_dir = None
        
        
    return serve_dir



##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### 
##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### 
##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### 
def get_point_level_info(one_point_sequence):
    '''
    Args:
    -----
    one_point_sequence [dict]: Dictionary
    
    Returns:
    --------
    dict of row to append into a dataframe
    
    *******************************************************
    Collects relevant information for a single rally point
    *******************************************************
    
    Notes:
    ------
    For a point sequence in a match, tidy information on relevant stats like serve speed
    or ball coordinates.
    '''
    
    # -- Get Serve Speed -----
    serve_speed_kph = one_point_sequence['ballSpeedFrench']
    if ( (serve_speed_kph == '0') | ( serve_speed_kph == 'NA' ) ):
        serve_speed_kph = one_point_sequence['returnSpeedFrench']
        
    #serve_speed_kph_v2 = one_point_sequence['ballSpeed']
    #if ( (serve_speed_kph_v2 == '0') | ( serve_speed_kph_v2 == 'NA' ) ):
    #    serve_speed_kph_v2 = one_point_sequence['returnSpeed']
       
    
    # -- Flag for whether we have tracking data on this point sequence -----
    is_track_avail = True
    if len(one_point_sequence['trajectoryData']) == 0 :
        is_track_avail = False
    
    # -- Serve coordinate at Net (can be used to calculate net clearance)
    z_net_serve = None
    x_net_serve = None
    y_net_serve = None
    
    if is_track_avail:
        
        try:
            served_ball_loc_net = one_point_sequence['trajectoryData'][2]
            
            if served_ball_loc_net['position'] == 'net':
                z_net_serve = served_ball_loc_net['z']
                x_net_serve = served_ball_loc_net['x']
                y_net_serve = served_ball_loc_net['y']
                
        except IndexError:
            pass
            #print('Index Error...')

            
    ##########################################################################        
    # -- Add ball location at contact of serve
    x_ball_serve_impact = None
    y_ball_serve_impact = None
    z_ball_serve_impact = None
    
    if is_track_avail :
        try:
            ball_loc_at_serve = one_point_sequence['trajectoryData'][0]
            
            if ball_loc_at_serve['position'] == 'hit':
                x_ball_serve_impact = ball_loc_at_serve['x']
                y_ball_serve_impact = ball_loc_at_serve['y']
                z_ball_serve_impact = ball_loc_at_serve['z']
                
        except IndexError:
            pass

            
            
    ##########################################################################  
    # Add return shots and serve plus 1 locations
    serve_return_dict = dict(
        serve_return_impact_x = None,
        serve_return_impact_y = None,
        serve_return_impact_z = None,
        serve_return_net_x = None,
        serve_return_net_y = None,
        serve_return_net_z = None,
        serve_return_bounce_x = None,
        serve_return_bounce_y = None,
        serve_return_bounce_z = None)
    
    #serve_plus1_dict = dict(
    #    serve_plus1_bounce_x = None,
    #    serve_plus1_bounce_y = None,
    #    serve_plus1_bounce_z = None
    #)
    
    
    if is_track_avail:
        serve_return_dict = collect_serve_return_locations( one_point_sequence['trajectoryData'] )
        #serve_plus1_dict =collect_serve_plus1_locations( one_point_sequence['trajectoryData'] )
    
    
    ##########################################################################
    
    
    # -- Identify whether serve bounce is Body, Wide, or Down the T -----
    serveBounceCordinate_y = one_point_sequence['serveBounceCordinate']['y']
    serve_dir = categorise_serve_direction(serveBounceCordinate_y)
    

    point_dict = dict(
        # -- Match situation information
        point_ID = one_point_sequence['pointId'],
        set_num = one_point_sequence['set'],
        game_num = one_point_sequence['game'], 
        point_num = one_point_sequence['point'],
        serve_num = one_point_sequence['serve'],
        
        # -- Players involved
        server_id = one_point_sequence['serverId'],
        returner_id = one_point_sequence['receiverId'],
        point_winner_id = one_point_sequence['scorerId'],
        court_side = one_point_sequence['court'],
        
        # Serve Stats
        serve_speed_kph = serve_speed_kph,
        #serve_speed_kph_v2 = serve_speed_kph_v2,
        serve_type = one_point_sequence['serveType'],
        #fault_distance_missed_ft = one_point_sequence['distanceOutsideCourt'],
        fault_distance_missed_m = one_point_sequence['distanceOutsideCourtFrench'],
        x_ball_serve_impact = x_ball_serve_impact,
        y_ball_serve_impact= y_ball_serve_impact,
        z_ball_serve_impact= z_ball_serve_impact,
        
        # How point ended
        rally_length = one_point_sequence['rallyLength'],
        point_end_type = one_point_sequence['pointEndType'],
        error_type = one_point_sequence['errorType'],
        trapped_by_net = one_point_sequence['trappedByNet'],

        last_stroke_type = one_point_sequence['strokeType'],
        last_hand = one_point_sequence['hand'],
        
        #last_strike_net_height_ft = one_point_sequence['heightAboveNet'],
        last_stroke_net_height_m = one_point_sequence['heightAboveNetFrench'],
        # 0 is ground height...height does not start on top of the net!!!
        
        winner_placement = one_point_sequence['winnerPlacement'],
        unforcedErrorPlacement = one_point_sequence['unforcedErrorPlacement'],
        is_break_point = one_point_sequence['breakPoint'],
        is_break_point_converted = one_point_sequence['breakPointConverted'],
        #runAroundForeHand = one_point_sequence['runAroundForeHand'],

        
        # Tracking info
        is_track_avail = is_track_avail,
        
        x_serve_bounce = one_point_sequence['serveBounceCordinate']['x'],
        y_serve_bounce = one_point_sequence['serveBounceCordinate']['y'],
        z_serve_bounce = one_point_sequence['serveBounceCordinate']['z'],
        serve_dir = serve_dir,
        z_net_serve = z_net_serve,
        x_net_serve = x_net_serve,
        y_net_serve = y_net_serve,
        
        # (initial) Ball coordinate on last shot 
        last_ball_impact_x = one_point_sequence['ballHitCordinate']['x'],
        last_ball_impact_y = one_point_sequence['ballHitCordinate']['y'],
        last_ball_impact_z = one_point_sequence['ballHitCordinate']['z'],
        
        # Ball coordinate on its last bounce of rally
        last_ball_bounce_x = one_point_sequence['ballBounceCordinate']['x'],
        last_ball_bounce_y = one_point_sequence['ballBounceCordinate']['y'],
        last_ball_bounce_z = one_point_sequence['ballBounceCordinate']['z'],
        
        # Server and Returner coordinates
        #server_coord_x = one_point_sequence['serverCordinate']['x'],
        #server_coord_y = one_point_sequence['serverCordinate']['y'],
        #server_coord_z = one_point_sequence['serverCordinate']['z'],
        #returner_coord_x = one_point_sequence['receiverCordinate']['x'],
        #returner_coord_y = one_point_sequence['receiverCordinate']['y'],
        #returner_coord_z = one_point_sequence['receiverCordinate']['z'],
        
        # serve return locations
        serve_return_impact_x = serve_return_dict['serve_return_impact_x'],
        serve_return_impact_y = serve_return_dict['serve_return_impact_y'],
        serve_return_impact_z = serve_return_dict['serve_return_impact_z'],
        serve_return_net_x = serve_return_dict['serve_return_net_x'],
        serve_return_net_y = serve_return_dict['serve_return_net_y'],
        serve_return_net_z = serve_return_dict['serve_return_net_z'],
        serve_return_bounce_x = serve_return_dict['serve_return_bounce_x'],
        serve_return_bounce_y = serve_return_dict['serve_return_bounce_y'],
        serve_return_bounce_z = serve_return_dict['serve_return_bounce_z'],
        
        # Serve plus 1 locations
        #serve_plus1_bounce_x = serve_plus1_dict['serve_plus1_bounce_x'],
        #serve_plus1_bounce_y = serve_plus1_dict['serve_plus1_bounce_y'],
        #serve_plus1_bounce_z = serve_plus1_dict['serve_plus1_bounce_z'],
        
        # unknowns
        spin_rpm = one_point_sequence['spin']
        #cruciality = one_point_sequence['cruciality'],
        #returnPlacement =  one_point_sequence['returnPlacement']
    )
    
    return point_dict


########################################################################################
########################################################################################
########################################################################################
def collect_serve_return_locations(trajectory_data_list):
    '''
    trajectory_data_list[list]: each element is a dictionary of ball trajectory (x,y,z)
    
    Returns dictionary of return shot at net and on the bounce
    '''
    
    # -- list of "position" keys for each trajectory instance
    position_keys_list = [ item['position'] for item in trajectory_data_list]

# -- 
#list(enumerate(position_keys_list))
# eg: [(0, 'hit'), (1, 'peak'), (2, 'net'), (3, 'last')]
    
    serve_return_impact_x = None
    serve_return_impact_y = None
    serve_return_impact_z = None
    serve_return_net_x = None
    serve_return_net_y = None
    serve_return_net_z = None
    serve_return_bounce_x = None
    serve_return_bounce_y = None
    serve_return_bounce_z = None
    
    
    try:
        # -- second instance of 'net' (i.e. the return net shot)
        serve_return_impact_index = [index for index, n in enumerate(position_keys_list) if n == 'hit'][1]
        serve_return_net_index = [index for index, n in enumerate(position_keys_list) if n == 'net'][1]
        serve_return_bounce_index = [index for index, n in enumerate(position_keys_list) if n == 'bounce'][1]

        serve_return_impact_x = trajectory_data_list[serve_return_impact_index]['x']
        serve_return_impact_y = trajectory_data_list[serve_return_impact_index]['y']
        serve_return_impact_z = trajectory_data_list[serve_return_impact_index]['z']
        
        serve_return_net_x = trajectory_data_list[serve_return_net_index]['x']
        serve_return_net_y = trajectory_data_list[serve_return_net_index]['y']
        serve_return_net_z = trajectory_data_list[serve_return_net_index]['z']

        serve_return_bounce_x = trajectory_data_list[serve_return_bounce_index]['x']
        serve_return_bounce_y = trajectory_data_list[serve_return_bounce_index]['y']
        serve_return_bounce_z = trajectory_data_list[serve_return_bounce_index]['z']
    
    except IndexError:
        #print('Tracking Data not available!')
        pass
        
        
    return dict(
        serve_return_impact_x = serve_return_impact_x,
        serve_return_impact_y = serve_return_impact_y,
        serve_return_impact_z = serve_return_impact_z,
        serve_return_net_x = serve_return_net_x,
        serve_return_net_y = serve_return_net_y,
        serve_return_net_z = serve_return_net_z,
        serve_return_bounce_x = serve_return_bounce_x,
        serve_return_bounce_y = serve_return_bounce_y,
        serve_return_bounce_z = serve_return_bounce_z)
    
    
def collect_serve_plus1_locations(trajectory_data_list):
    '''
    trajectory_data_list[list]: each element is a dictionary of ball trajectory (x,y,z)
    
    Returns dictionary of return shot at net and on the bounce
    '''
    
    # -- list of "position" keys for each trajectory instance
    position_keys_list = [ item['position'] for item in trajectory_data_list]

# -- 
#list(enumerate(position_keys_list))
# eg: [(0, 'hit'), (1, 'peak'), (2, 'net'), (3, 'last')]
    

    serve_plus1_bounce_x = None
    serve_plus1_bounce_y = None
    serve_plus1_bounce_z = None
    
    
    try:
        # -- Third instance of 'bounce' (i.e. the return net shot)
        serve_plus1_bounce_index = [index for index, n in enumerate(position_keys_list) if n == 'bounce'][2]


        serve_plus1_bounce_x = trajectory_data_list[serve_plus1_bounce_index]['x']
        serve_plus1_bounce_y = trajectory_data_list[serve_plus1_bounce_index]['y']
        serve_plus1_bounce_z = trajectory_data_list[serve_plus1_bounce_index]['z']
    
    except IndexError:
        #print('Tracking Data not available!')
        pass
        
        
    return dict(
        serve_plus1_bounce_x = serve_plus1_bounce_x,
        serve_plus1_bounce_y = serve_plus1_bounce_y,
        serve_plus1_bounce_z = serve_plus1_bounce_z)
    


##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### 
##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### 
##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### 
def get_match_point_level_info(raw_json_file):
    '''
    Args:
    -----
    one_point_sequence [dict]: Dictionary
    
    Returns:
    --------
    pandas DataFrame
    
    Collect all play-by-play information for a match into a pandas DataFrame
    '''
    all_tracking_data_dict = raw_json_file['courtVisionData'][0]['pointsData']
    
    data_list = []
    for point_id_key in sorted(all_tracking_data_dict.keys()):
        #print(point_id_key)
        data_list.append( get_point_level_info( all_tracking_data_dict[point_id_key] ) )
    
    match_point_df = pd.DataFrame(data_list)
    
    # Sort Dataframe by Set Number, Game number, Point Number, Serve Number
    match_point_df[['set_num', 'game_num', 'point_num', 'serve_num']] = match_point_df[['set_num', 'game_num', 'point_num', 'serve_num']].astype(int)


    match_point_df.sort_values(by = ['set_num', 'game_num', 'point_num', 'serve_num'], inplace = True)
    
    
    # -- Fix court side categorization (Ad / Deuce court)
    match_point_df['court_side'] = np.where(match_point_df['point_num'] %2 == 0,
                                            'AdCourt','DeuceCourt')
    
    # -- Reset row indices
    match_point_df.reset_index(drop=True, inplace=True)

    # -- Add Fault Flag
    is_fault = np.where(np.isin(match_point_df['point_end_type'], ['Faulty Serve', 'DoubleFault']),
                                          1, 0)
    
    # |--> some Faults are coded as 'NA'
    is_fault_v2 = np.where(match_point_df[['set_num', 'game_num', 'point_num']].duplicated(),1,0).tolist()
    is_fault_v2_order = np.array(is_fault_v2[1:] + [0])
    for serve_index in range(len(is_fault)):
        if( (is_fault_v2_order[serve_index] == 1) & (is_fault[serve_index] != 1) ):
            is_fault[serve_index] = 1
    
    match_point_df['is_fault'] = is_fault

    
    # -- Add Double Fault Flag
    match_point_df['is_doublefault'] = np.where(np.isin(match_point_df['point_end_type'], ['DoubleFault']),
                                                1, 0)
    # -- Add Tiebreak flag
    match_point_df['is_tiebreak'] = np.where(match_point_df['game_num'] > 12,
                                             1, 0)
    
    # -- Add ace flag
    match_point_df['is_ace'] =  np.where(match_point_df['point_end_type'] == 'Ace',1,0)
    # -- Add previous serve was ace / double fault flag
    
    match_point_df['is_prev_doublefault'] = np.insert(arr = match_point_df['is_doublefault'][:-1].values, obj=0, values=0)
    match_point_df['is_prev_ace'] = np.insert(arr = match_point_df['is_ace'][:-1].values, obj=0, values=0)
    
    # -- Add server score & returner score columns
    is_score_avail = False
    try: 
        score_df = add_server_and_returner_scores(match_point_df[['point_num', 'is_fault', 'is_doublefault', 'server_id', 'returner_id','point_winner_id', 'is_tiebreak']])
        
        is_score_avail = True
        
    except IndexError:
        print('Could not get score columns...')
        score_df = pd.DataFrame(dict(server_score = [None] * match_point_df.shape[0],
                                     returner_score = [None] * match_point_df.shape[0]))
        
    match_point_df = pd.concat([match_point_df, score_df], axis=1)
    
    # -- Add cumulative games won and sets won
    
    if is_score_avail:
        try:
            match_point_df =  add_cum_games_and_sets(match_point_df)
        except ValueError:
            pass
            #match_point_df = pd.DataFrame([])
    
    
    # -- Remove Duplicate rows
    match_point_df.drop_duplicates(inplace=True)
    # -- Reset row indices
    match_point_df.reset_index(drop=True, inplace=True)
    
    return match_point_df



##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### 
##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### 
##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### 
def add_server_and_returner_scores(match_pbp):
    '''
    Args:
    -----
    match_pbp [pandas DataFrame]
    
    Returns:
    --------
    pandas DataFrame with 2 new columns: server score and returner score at the beginning of the point
    
    '''
    
    
    server_score_vec = []
    returner_score_vec = []


    for point_id in range(match_pbp.shape[0]):
        #print(point_id)

        # -- If first point of a game, set both scores to 0
        point_num = match_pbp['point_num'][point_id]
        if point_num == 1:
            server_score_vec.append(0)
            returner_score_vec.append(0)
            continue

        # -- Get server & returner's current scores
        current_server_score = server_score_vec[point_id -1]
        current_returner_score = returner_score_vec[point_id-1]
        
        
        # -- Sometimes, Faults aren't properly encoded... Ex sometimes coded as 'NA'
        prev_point_num = match_pbp['point_num'][point_id-1]
        if point_num == prev_point_num:
            is_fault = 1
        

        # -- If 1st Serve Fault, score does not change
        is_fault = match_pbp['is_fault'][point_id-1]
        is_doublefault = match_pbp['is_doublefault'][point_id-1]
        if ((is_fault ==1) & (is_doublefault == 0)):
            server_score_vec.append(current_server_score)
            returner_score_vec.append(current_returner_score)
            continue
            



        # -- Get IDs
        server_id = match_pbp['server_id'][point_id-1]
        returner_id = match_pbp['returner_id'][point_id-1]
        winner_id = match_pbp['point_winner_id'][point_id-1]


        # -- Deal with Tiebreaks
        is_tiebreak = match_pbp['is_tiebreak'][point_id-1]

        if(is_tiebreak == 1):
        
            next_server_id = match_pbp['server_id'][point_id]
            did_server_change = np.logical_not(next_server_id == server_id)


            if server_id == winner_id:
                update_server_score = current_server_score + 1

                # -- If server wins and changes, then score gets added to the returner
                if did_server_change:
                    server_score_vec.append(current_returner_score)
                    returner_score_vec.append(update_server_score)
                else:
                    server_score_vec.append(update_server_score)
                    returner_score_vec.append(current_returner_score)

            else: # -- If returner wins and changes, then score gets added to the server
                update_returner_score = current_returner_score + 1

                if did_server_change:
                    server_score_vec.append(update_returner_score)
                    returner_score_vec.append(current_server_score)

                else:
                    server_score_vec.append(current_server_score)
                    returner_score_vec.append(update_returner_score)
            continue


        if server_id == winner_id:
            update_server_score = current_server_score + 1
            server_score_vec.append(update_server_score) 
            returner_score_vec.append(current_returner_score)


        else:
            update_returner_score = current_returner_score + 1
            server_score_vec.append(current_server_score)
            returner_score_vec.append(update_returner_score)

    score_vec_dict = dict(server_score = server_score_vec,
                          returner_score = returner_score_vec)
    #match_pbp['server_score'] = server_score_vec
    #match_pbp['returner_score'] = returner_score_vec
    score_df = pd.DataFrame(score_vec_dict)
    
    #return match_pbp
    return score_df



##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### 
##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### 
##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### 
def add_cum_games_and_sets(match_pbp):
    
    '''
    Args:
    -----
    match_pbp [pandas DataFrame]
    
    Returns:
    --------
    pandas DataFrame with cumulative games and sets won
    
    '''
    
    # Arbitrarily set the 1st server as 'player1' and the other as 'player2'
    player1 = match_pbp['server_id'][0]
    player2 = match_pbp['returner_id'][0]

    # Ids for the beginning point of each game 
    # By virtue of the data, some points might begin with a 2nd serve!!!! 
    #beginning_point_ids = np.where((match_pbp['point_num'] == 1) & (match_pbp['serve_num'] == 1))[0]
    beginning_point_ids = match_pbp[match_pbp['point_num'] == 1][['set_num', 'game_num', 'serve_num']].drop_duplicates(subset=['set_num', 'game_num'], keep = 'first').index


    # Ids for the last point of each game
    last_point_ids = np.asarray(beginning_point_ids)[1:] - 1

    # Dataframe of all last points played
    last_points_df = match_pbp.loc[last_point_ids] 

    # Add indicator columns of whether server or returner won the last point of each game
    last_points_df['server_game_won'] = np.where(last_points_df['server_score'] > last_points_df['returner_score'],
                                                 1,0)


    last_points_df['returner_game_won'] = np.where(last_points_df['server_game_won']  == 0,
                                                   1,0)

    last_points_df.reset_index(drop=True, inplace=True)


    # Calculate the Cumulative number of games won
    p1_cum_games = []
    p2_cum_games = []


    for set_number in np.unique(last_points_df['set_num']):
        p1_game_vec = [0]
        p2_game_vec = [0]

        # For each set, calculate the cumulative number of games won for each player    
        set_pbp = last_points_df[last_points_df['set_num'] == set_number]
        set_pbp.reset_index(drop=True, inplace=True)

        for point_id in range(set_pbp.shape[0]):
            if set_pbp['server_game_won'][point_id] == 1:
                 winner_id = set_pbp['server_id'][point_id]

            if set_pbp['returner_game_won'][point_id] == 1:
                winner_id = set_pbp['returner_id'][point_id]


            if winner_id == player1:
                p1_game_vec.append(p1_game_vec[point_id] +1)
                p2_game_vec.append(p2_game_vec[point_id])

            elif winner_id == player2:
                p1_game_vec.append(p1_game_vec[point_id])
                p2_game_vec.append(p2_game_vec[point_id]+1)
            else:
                continue

        p1_cum_games.append(p1_game_vec)
        p2_cum_games.append(p2_game_vec)

        p1_cum_games_np = np.array([item for sublist in p1_cum_games for item in sublist])
        p2_cum_games_np = np.array([item for sublist in p2_cum_games for item in sublist])

        # Remove Cumulative games that denote final game of a set
        # Ex: A set that is 6-0 is done, and won't be required for the calculation of point importance
        # Note: Roland Garros uses an ADVANTAGE SET
        last_set = match_pbp['set_num'][match_pbp.shape[0]-1]
        last_game = match_pbp['game_num'][match_pbp.shape[0]-1]

        absolute_diff = abs(p1_cum_games_np - p2_cum_games_np)
        #last_game_ids = np.cumsum( np.array(match_pbp.groupby('set_num')['game_num'].max()+1))
        last_game_ids = np.logical_or( np.logical_or(p1_cum_games_np >6, p2_cum_games_np >6),
                                       np.logical_or(np.logical_and(p1_cum_games_np ==6, absolute_diff >=2),
                                                     np.logical_and(p2_cum_games_np ==6, absolute_diff >=2))
                 )
        p1_cum_games_to_add = p1_cum_games_np[np.logical_not(last_game_ids)]
        p2_cum_games_to_add = p2_cum_games_np[np.logical_not(last_game_ids)]

    # -- Left join play-by-play data with columns denoting cumulative number of games won by each player
    games_df = match_pbp.loc[beginning_point_ids]
    games_df['player1'] = player1
    games_df['player2'] = player2
    
    # -- Roland Garros plays an Advantage Set!!!! **** This needs fixing
    games_df = games_df[games_df['game_num'] <= 13]
    
    games_df['p1_cum_games'] = p1_cum_games_to_add 
    games_df['p2_cum_games'] = p2_cum_games_to_add 

    added_cum_games_df = pd.merge(left = match_pbp,
                                  right = games_df[['game_num','set_num','player1','player2','p1_cum_games','p2_cum_games']],
                                  how="left",
                                  on = ['game_num','set_num'])

    # -- add cumulative sets won

    # Find indices where we change set
    set_change_id = np.delete(np.array(added_cum_games_df[added_cum_games_df['set_num'].diff() != 0].index),0)
    last_points_in_set_df = added_cum_games_df.loc[set_change_id-1]
    last_points_in_set_df.reset_index(drop=True, inplace=True)

    p1_cum_sets = [0]
    p2_cum_sets = [0]

    for set_index in range(last_points_in_set_df.shape[0]):
        # -- Figure out who won each set
        if last_points_in_set_df['server_score'][set_index] > last_points_in_set_df['returner_score'][set_index]:
            set_winner_id = last_points_in_set_df['server_id'][set_index]

        if last_points_in_set_df['server_score'][set_index] < last_points_in_set_df['returner_score'][set_index]:
            set_winner_id = last_points_in_set_df['returner_id'][set_index]

        if set_winner_id == player1:
            p1_cum_sets.append(p1_cum_sets[set_index] + 1) 
            p2_cum_sets.append(p2_cum_sets[set_index])

        if set_winner_id == player2:
            p1_cum_sets.append(p1_cum_sets[set_index]) 
            p2_cum_sets.append(p2_cum_sets[set_index] + 1)


    changeover_set_df = added_cum_games_df.loc[np.append(0, set_change_id)]
    changeover_set_df.reset_index(drop=True, inplace=True)
    changeover_set_df['p1_cum_sets'] = p1_cum_sets
    changeover_set_df['p2_cum_sets'] = p2_cum_sets

    added_cum_games_and_sets_df = pd.merge(left = added_cum_games_df,
                                           right = changeover_set_df[['set_num','player1','player2','p1_cum_sets','p2_cum_sets']],
                                           how="left",
                                           on = ['set_num','player1','player2' ])
    
    return(added_cum_games_and_sets_df)




##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### 
##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### 
##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### ----- ##### 