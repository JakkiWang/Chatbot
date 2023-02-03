
# emoji mapping
happy_emoticons = [":grinning_face:", ":grinning_face_with_big_eyes:", ":grinning_face_with_smiling_eyes:", ":beaming_face_with_smiling_eyes:",
				   ":grinning_squinting_face:", ":rolling_on_the_floor_laughing:", ":face_with_tears_of_joy:", ":slightly_smiling_face:",
				   ":winking_face:", ":smiling_face_with_smiling_eyes:", ":smiling_face_with_halo:", ":smiling_face_with_hearts:",
				   ":smiling_face_with_hear t -eyes:", ":sta r -struck:", ":face_blowing_a_kiss:", ":kissing_face:", ":smiling_face:",
				   ":kissing_face_with_closed_eyes:", ":kissing_face_with_smiling_eyes:", ":smiling_face_with_tear:", ":face_savoring_food:",
				   ":face_with_tongue:", ":winking_face_with_tongue:", ":zany_face:", ":squinting_face_with_tongue:",
				   ":mone y -mouth_face:",":smiling_face_with_open_hands:",":smirking_face:",":grimacing_face:",":saluting_face:",
				   ":lying_face:",":cowboy_hat_face:",":partying_face:",":smiling_face_with_sunglasses:",":nerd_face:",
				   ":face_holding_back_tears:", ":ghost:",":alien:",":alien_monster:",":robot:",":grinning_cat:",
				   ":grinning_cat_with_smiling_eyes:",":cat_with_tears_of_joy:",":smiling_cat_with_hear t -eyes:",
				   ":cat_with_wry_smile:",":kissing_cat:", ":se e -n o -evil_monkey:",":hea r -n o -evil_monkey:",
				   ":spea k -n o -evil_monkey:",":kiss_mark:",":love_letter:",":heart_with_arrow:",":heart_with_ribbon:",
				   ":sparkling_heart:",":growing_heart:",":beating_heart:",":revolving_hearts:",":two_hearts:"]

moderate_emoticons = [":grinning_face_with_sweat:", ":upside-down_face:",":face_with_hand_over_mouth:",":face_with_open_eyes_and_hand_over_mouth:",
					":face_with_peeking_eye:",":shushing_face:",":thinking_face:", ":face_with_open_mouth:", ":relieved_face:",":pensive_face:",
					":sleepy_face:",":drooling_face:",":sleeping_face:",":exploding_head:",":face_with_monocle:",":face_with_open_mouth:",
					":hushed_face:",":astonished_face:",":flushed_face:",":pleading_face:",":yawning_face:"
					]

slightly_bad = [":melting_face:", ":zippe r -mouth_face:",":face_with_raised_eyebrow:",":neutral_face:",":expressionless_face:",
				":face_without_mouth:",":dotted_line_face:",":face_without_mouth:",":fog:", ":dashing_away:",":confused_face:",
				":frowning_face_with_open_mouth:", ":anguished_face:",	":weary_cat:",":crying_cat:",":pouting_cat:"]

bad_emoticons = [":unamused_face:", ":face_with_rolling_eyes:",":face_with_medical_mask:",":face_with_thermometer:",
				 ":face_with_hea d -bandage:",":nauseated_face:",":face_vomiting:",":sneezing_face:",":hot_face:",":cold_face:",
				 ":woozy_face:",":face_with_crosse d -out_eyes:",":face_with_crosse d -out_eyes:",":dizzy:",":disguised_face:",
				 ":face_with_diagonal_mouth:",":worried_face:",":slightly_frowning_face:",":frowning_face:",":fearful_face:",
				 ":anxious_face_with_sweat:",":sad_but_relieved_face:",":crying_face:",":loudly_crying_face:",":face_screaming_in_fear:",
				 ":confounded_face:",":persevering_face:",":disappointed_face:",":downcast_face_with_sweat:",":weary_face:",
				 ":tired_face:",":face_with_steam_from_nose:",":enraged_face:",":angry_face:",":face_with_symbols_on_mouth:",
				 ":smiling_face_with_horns:",":angry_face_with_horns:",":skull:",":skull_and_crossbones:",":pile_of_poo:",
				 ":ogre:",":goblin:"
]


emoji_mapping = {}
for e in happy_emoticons:
	emoji_mapping[e] = "positive"
for e in moderate_emoticons:
	emoji_mapping[e] = "moderate"
for e in slightly_bad:
	emoji_mapping[e] = "moderate_negative"
for e in bad_emoticons:
	emoji_mapping[e] = "negative"


# predicted label mapping
POS_EMO = ["admiration", "joy", "approval", "gratitude", "excitement", "pride", "love", "realization", "desire", "caring", "optimism", "amusement"]
NEU_EMO = ["neutral", "surprise", "relief", "curiosity"]
NEG_EMO = ["annoyance", "disappointment", "sadness", "confusion", "disapproval", "anger", "nervousness", "fear", "disgust", "grief", "remorse", "embarrassment"]

# emoji score mapping
emoji_score_mapping = {"positive": 10, "moderate": 5, "moderate_negative": 2.5, "negative": 0.1}

# age group mapping
age_group_mapping = {0: [9,10,11,12],
					 1: [13,14,15],
					 2: [16,17,18],
					 3: [19,20,21,22,23],
					 4: [24,25,26,27,28,29],
					 5: [30, 31, 32, 33, 34, 35],
					 6: [36, 37, 38, 39, 40],
					 7: [41, 42, 43, 44, 45, 46],
					 8: [47, 48, 49, 50, 51, 52, 53, 54, 55],
					 9: [56, 57, 58, 59, 60, 61, 62],}
