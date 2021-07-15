# ### --- ### --- ### --- ### --- ### --- ### --- ### --- ### --- ### --- ### --- ### 
### Last update: June 26th, 2021
# ### --- ### --- ### --- ### --- ### --- ### --- ### --- ### --- ### --- ### --- ### 

# ### --- ### --- ### --- ### --- ### 
### -- GOALS -----
# ### --- ### --- ### --- ### --- ### 
### * Create data frame: | Player Name | Player ID | Country | Handedness | 

library(dplyr)
match_data_log <- read.csv("./catalogue_all_matches_available.csv")


# -- Remove Doubles for now (9 obs. removed) -----
match_data_log <- match_data_log %>%
  filter(!grepl("Doubles",match_type)) %>%
  select(player1, player1_id, player1_country, player2, player2_id, player2_country, league) %>%
  mutate(player1 = gsub('\\s+', '', player1),
         player2 = gsub('\\s+', '', player2))

player1_df <- match_data_log[,c('player1', 'player1_id','player1_country', 'league')]
colnames(player1_df) <- c('name', 'id', 'country', 'league')

player2_df <- match_data_log[,c('player2', 'player2_id', 'player2_country', 'league')]
colnames(player2_df) <- c('name', 'id','country', 'league')

player_df <- rbind(player1_df, 
                   player2_df )


# -- Manually change some names to match player height names -----
player_df[player_df$name == 'JM.DELPOTRO','name'] <- 'J.DELPOTRO'
player_df[player_df$name == 'JL.STRUFF','name'] <- 'J.STRUFF'
player_df[player_df$name == 'JW.TSONGA','name'] <- 'J.TSONGA'
player_df[player_df$name == 'PH.HERBERT','name'] <- 'P.HERBERT'
player_df[player_df$name == 'DE.GALAN','name'] <- 'D.GALAN'
player_df[player_df$name == 'AK.SCHMIEDLOVA','name'] <- 'A.SCHMIEDLOVA'
player_df[player_df$name == 'C.SUÁREZNAVARRO','name'] <- 'C.SUAREZNAVARRO'
player_df[player_df$name == 'PM.TIG','name'] <- 'P.TIG'
player_df[player_df$name == 'F.AUGER-ALIASSIME','name'] <- 'F.AUGERALIASSIME'
player_df[player_df$name == 'JI.LONDERO','name'] <- 'J.LONDERO'


# -- (Eventually) Add how many matches we have available for each player
num_matches_df <-
player_df %>%
  mutate(name = toupper(name)) %>%
  group_by(name) %>%
  summarise(num_matches = n()) %>%
  arrange(desc(num_matches))

player_df <- player_df[!duplicated(player_df),] %>%
  mutate(name = toupper(name)) %>%
  arrange(name)


summary_data <- player_df %>%
  left_join(num_matches_df) %>%
  arrange(desc(num_matches)) %>%
  group_by(name)  %>% 
  filter(row_number() == 1)

write.csv(summary_data,
          './player_data_available.csv',
          row.names = FALSE)

write.csv(player_df,
          'player_ids.csv',
          row.names = FALSE)



# -- Challenge: AO and RG use different player ID codes -----
# --> Eventually, to join player names to AO and RG data, we'll need both player ID formats.
# --> Soln: Remove duplicate names; keep first instance (RG's integer ID code)
# player_df <- player_df %>%
#   mutate(name = toupper(name)) %>%
#   arrange(league, name, id) %>%
#   group_by(name)  %>% 
#   filter(row_number() == 1)


# -- Check: Are there any names that repeat? -----
n_occur <- data.frame(table(player_df$id))
n_occur[n_occur$Freq > 1,]

# player_df %>%
#   filter(id %in% c('11713', '21623', '23386', '6291'))


# -- Add Player Handedness Data -----
atp_hand_df <- read.csv('../data/official_atp_handedness_2020.csv')
wta_hand_df <- read.csv('../data/official_wta_handedness_2020.csv')

# -- convert name to be entirely UPPERCASE
atp_hand_df$player_name <- toupper(atp_hand_df$player_name)
wta_hand_df$player_name <- toupper(wta_hand_df$player_name)

# -- get first letter of first name and entire last name
atp_first_letter <- substr(atp_hand_df$player_name, 1, 1)
atp_last_name <- stringr::str_extract(atp_hand_df$player_name, '[^ ]+$')

wta_first_letter <- substr(wta_hand_df$player_name, 1, 1)
wta_last_name <- stringr::str_extract(wta_hand_df$player_name, '[^ ]+$')

# -- Add modified name format to dataframe
atp_hand_df$new_name <- paste(atp_first_letter, '.', atp_last_name, sep = '')
wta_hand_df$new_name <- paste(wta_first_letter, '.', wta_last_name, sep = '')

# -- Fix some names manually (R.BAUTISTAAGUT; P.CARRENOBUSTA; J.DELPOTRO)
atp_hand_df[atp_hand_df$player_name == 'ROBERTO BAUTISTA AGUT','new_name'] <- 'R.BAUTISTAAGUT'
atp_hand_df[atp_hand_df$player_name == 'PABLO CARRENO BUSTA','new_name'] <- 'P.CARRENOBUSTA'
atp_hand_df[atp_hand_df$player_name == 'JUAN MARTIN DEL POTRO','new_name'] <- 'J.DELPOTRO'
atp_hand_df[atp_hand_df$player_name == 'DANIEL ELAHI GALAN','new_name'] <- 'D.GALAN'
atp_hand_df[atp_hand_df$player_name == 'ROBERTO CARBALLES BAENA','new_name'] <- 'R.CARBALLESBAENA'
atp_hand_df[atp_hand_df$player_name == 'ALEJANDRO DAVIDOVICH FOKINA','new_name'] <- 'A.DAVIDOVICHFOKINA'
atp_hand_df[atp_hand_df$player_name == 'ALEX DE MINAUR','new_name'] <- 'A.DEMINAUR'
atp_hand_df[atp_hand_df$player_name == 'ALBERT RAMOS','new_name']  <- 'A.RAMOS-VINOLAS'
atp_hand_df[atp_hand_df$player_name == 'FELIX AUGER ALIASSIME','new_name'] <- 'F.AUGERALIASSIME'

wta_hand_df[wta_hand_df$player_name == 'KAROLINA PLISKOVA','new_name'] <- 'KA.PLISKOVA'
wta_hand_df[wta_hand_df$player_name == 'KRISTYNA PLISKOVA','new_name'] <- 'KR.PLISKOVA'
wta_hand_df[wta_hand_df$player_name == 'ANNA KAROLINA SCHMIEDLOVA','new_name'] <- 'A.SCHMIEDLOVA'
wta_hand_df[wta_hand_df$player_name == 'SARA SORRIBES TORMO','new_name'] <- 'S.SORRIBESTORMO'
wta_hand_df[wta_hand_df$player_name == 'PATRICIA MARIA TIG','new_name'] <- 'P.TIG'

atp_and_wta_handedness <- rbind(atp_hand_df %>% select(new_name, player_handedness),
                                wta_hand_df %>% select(new_name, player_handedness))



# -- Add new columns to player_df
player_df <- player_df %>%
  left_join(atp_and_wta_handedness,
            by = c('name' = 'new_name')) %>%
  arrange(league, name) %>% 
  distinct()

write.csv(player_df,
          './data/player_id_df.csv',
          row.names = FALSE)
