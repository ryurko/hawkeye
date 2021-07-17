# -- Script example collecting all of Djokovic's match data -----

library(dplyr)

# -- Load Player ID data
player_df <- read.csv('./misc/player_ids.csv')
# -- Load all matches available data
available_matches <- read.csv('./misc/catalogue_all_matches_available.csv')

# -- Pull Djokovic's IDs
djokovic_ids <-
player_df %>%
  filter(name =='N.DJOKOVIC') %>%
  pull(id)

# -- Get all Djokovic's match IDs
djokovic_match_ids <- 
available_matches %>%
  filter( (player1_id %in% djokovic_ids) | (player2_id %in% djokovic_ids) ) %>%
  pull(match_id)



# -- Collect all play-by-play data for Djokovic ----
data_list = list()
index = 1
for(filename in list.files('play_by_play/')){
  if(filename %in% paste0(djokovic_match_ids, '_pbp.csv')){
    match_df <- read.csv(paste0('./play_by_play/', filename))
    
    match_df$match_id <- djokovic_match_ids[which((filename == paste0(djokovic_match_ids, '_pbp.csv')))]
    data_list[[index]] <- match_df
    index = index + 1
    
  }}


djokovic_pbp <- do.call(rbind, data_list)

# -- add player names
djokovic_pbp <-
djokovic_pbp %>%
  left_join(player_df %>% 
              select(name, id),
            by = c('server_id' = 'id')) %>%
  rename(server_name = name) %>%
  left_join(player_df %>% 
              select(name, id),
            by = c('returner_id' = 'id')) %>%
  rename(returner_name = name)
  
  
# -- Collect all rally tracking data for Djokovic ----
data_list_track = list()
index = 1
for(filename in list.files('ball_trajectory/')){
  if(filename %in% paste0(djokovic_match_ids, '_ball_trajectory.csv')){
    
    track_data <- read.csv(paste0('./ball_trajectory/', filename))
    track_data$match_id <- djokovic_match_ids[which((filename == paste0(djokovic_match_ids, '_ball_trajectory.csv')))]
    data_list_track[[index]] <- track_data
    index = index + 1
    
  }}

djokovic_track <- do.call(rbind, data_list_track)


# -- Join these data sources together ----
all_djokovic_data <- 
djokovic_track %>%
  select(-c(set_num, game_num, point_num, serve_num )) %>%
  left_join(djokovic_pbp,
            by = c('match_id' = 'match_id',
                   'point_ID' = 'point_ID'))

write.csv(all_djokovic_data, 'all_djokovic_data.csv', row.names = FALSE)
