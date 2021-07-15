### Data Dictionary


* `point_ID`: Character point ID
* `set_num`: Set Number
* `game_num`: Game Number
* `point_num`: Point number WITHIN a game (always starts at 1)
* `serve_num`: Serve Number (1,2). Lets are not tracked.
* `server_id`: 'Server ID
* `returner_id`: Returner ID
* `point_winner_id`: Point Winner ID (either serverID or returnerID)
* `court_side`: Serve Court ('AdCourt' or 'DeuceCourt')
* `serve_speed_kph`: Serve Speed in Kilometers per Hour
* `serve_type`:'Flat', 'Pronated', 'Slice', 'Unclassified'
* `fault_distance_missed_m`: If serve was fault, by how much did it miss? In Metres
* `(x,y,z)_ball_serve_impact`: Location of where the serve ball was struck.
* `rally_length`: Length of rally (including serve)
* `point_end_type`: How did rally end? Ex: Fault, Unforced/Forced error, Winner
* `error_type`: If point ended in an error, which type? Ex: Net, Wide, Long
* `trapped_by_net`: *I think* Boolean for whether shot was net error?
* `slast_troke`: Type of stroke on last shot of rally. Ex: Ground, Passing, Drop. "Last shot" means any last recorded shot (winner, error, etc)
* `last_hand`: Handedness on last shot.
* `last_stroke_net_height_m`: Ball height at net on last shot of rally (in metres).
* `winner_placement`: Cross Court or Down the Line
* `unforcedErrorPlacement`: If shot error, what type? Wide, Net, Long. This is the same as `error_type`?
* `is_break_point`: Boolean
* `is_break_point_converted`: Boolean
* `runAroundForeHand`: Boolean
* `is_track_avail`: Boolean. Indicates whether ball tracking data is available for this rally sequence. 
* `(x,y,z)_serve_bounce`: coordinates of serve bounce
* `serve_dir`: Serve Direction (T, Wide, Body)
* `(x,y,z)_net_serve`: coordinates of serve ball as it reached the net
* `last_ball_impact_(x,y,z)`: Coordinates of last location ball was hit
* `last_ball_bounce_(x,y,z)`: coordinates of last ball bounce
* `serve_return_impact_(x,y,z)`: coordinates of where the returner made contact with serve
* `serve_return_net_(x,y,z)`: coordinates of where the serve-return shot reached the net
* `serve_return_bounce_(x,y,z)`: coordinates of where the serve-return shot landed
* `spin_rpm`: Ball spin on last rally shot
* `is_fault`: 0 = Not fault; 1= Fault 
* `is_doublefault`: 0 = Not doublefault; 1= doublefault 
* `is_tiebreak`: Indicator for current point being a tiebreak
* `is_ace`: Indicator if serve is an ace
* `is_prev_doublefault`: Indicator if serve is doublefault
* `is_prev_ace`: Indicator if previous serve was an ace
* `server_score`: 
* `returner_score`:
* `player1`:
* `player2`:
* `p1_cum_games`:
* `p2_cum_games`:
* `p1_cum_sets`:
* `p2_cum_sets`: