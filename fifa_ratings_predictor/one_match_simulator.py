import argparse

import numpy as np
from fifa_ratings_predictor.model import NeuralNet
from fifa_ratings_predictor.data_methods import normalise_features


def one_match_simulator(home_goalkeeper, home_defenders, home_midfielders, home_forwards, away_goalkeeper,
                        away_defenders, away_midfielders, away_forwards, match_data,
                        model_name='/Users/offera/Desktop/Personal Projects/SmartBets/fifa_ratings_predictor'
                                   '/models/E0'
                                   '/deep2'):
    home_defenders = home_defenders + [0] * (6 - len(home_defenders))
    away_defenders = away_defenders + [0] * (6 - len(away_defenders))
    home_midfielders = home_midfielders + [0] * (7 - len(home_midfielders))
    away_midfielders = away_midfielders + [0] * (7 - len(away_midfielders))
    home_forwards = home_forwards + [0] * (4 - len(home_forwards))
    away_forwards = away_forwards + [0] * (4 - len(away_forwards))

    home_position = match_data[0]
    home_points = match_data[1]
    home_played = match_data[2]
    home_goals_total = match_data[3]
    home_conceded_total = match_data[4]
    home_form = match_data[5]
    away_position = match_data[6]
    away_points = match_data[7]
    away_played = match_data[8]
    away_goals_total = match_data[9]
    away_conceded_total = match_data[10]
    away_form = match_data[11]

    home_feature_vector = home_goalkeeper + home_defenders + home_midfielders + home_forwards + [home_position, home_points, home_played, home_goals_total, home_conceded_total, home_form]
    away_feature_vector = away_goalkeeper + away_defenders + away_midfielders + away_forwards + [away_position, away_points, away_played, away_goals_total, away_conceded_total, away_form]

    feature_vector = normalise_features(np.array(home_feature_vector + away_feature_vector)).reshape(1, 48)

    net = NeuralNet()
    probability = net.predict(feature_vector, model_name)

    return probability[0]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--home-goalkeeper',
        type=int,
        nargs=1,
        required=True,
        help="""\
      An integer between 0 and 100 for the rating of the goalkeeper.\
      """
    )
    parser.add_argument(
        '--home-defenders',
        type=int,
        nargs='+',
        required=False,
        help="""\
          A number of integers between 0 and 100 for the ratings of the defenders.\
          """
    )
    parser.add_argument(
        '--home-midfielders',
        type=int,
        nargs='+',
        required=False,
        help="""\
              A number of integers between 0 and 100 for the ratings of the midfielders.\
              """
    )
    parser.add_argument(
        '--home-forwards',
        type=int,
        nargs='+',
        required=False,
        help="""\
                  A number of integers between 0 and 100 for the ratings of the forwards.\
                  """
    )
    parser.add_argument(
        '--away-goalkeeper',
        type=int,
        nargs=1,
        required=True,
        help="""\
          An integer between 0 and 100 for the rating of the goalkeeper.\
          """
    )
    parser.add_argument(
        '--away-defenders',
        type=int,
        nargs='+',
        required=False,
        help="""\
              A number of integers between 0 and 100 for the ratings of the defenders.\
              """
    )
    parser.add_argument(
        '--away-midfielders',
        type=int,
        nargs='+',
        required=False,
        help="""\
                  A number of integers between 0 and 100 for the ratings of the midfielders.\
                  """
    )
    parser.add_argument(
        '--away-forwards',
        type=int,
        nargs='+',
        required=False,
        help="""\
                      A number of integers between 0 and 100 for the ratings of the forwards.\
                      """
    )
    # parser.add_argument(
    #     '--model-name',
    #     type=str,
    #     required=False,
    #     help="""\
    #                       Model path\
    #                       """
    # )

    arguments, _ = parser.parse_known_args()

    print(one_match_simulator(**vars(arguments)))

    # [0.42155302 0.2851767  0.29327026]
