import pandas as pd
import argparse
import csv
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--threshold', type=float,
                    help='a float specifying the output threshold')
parser.add_argument('-lweight', type=float,
                    help='lightGBM predition weight')
parser.add_argument('-xweight', type=float,
                    help='XGBoost predition weight')

args = parser.parse_args()
if args.threshold:
	threshold = args.threshold
else:
	threshold = 0.18

if args.lweight:
	lightGBM_weight = args.lweight
else:
	lightGBM_weight = 1

if args.xweight:
	XGBoost_weight = args.xweight
else:
	XGBoost_weight = 0

DIR = '../data/'

print('###\tUsing a threshold of {} for predition output\t###'.format(threshold))
print('###\tlightGBM_weight: {}, XGBoost_weight:{}'.format(lightGBM_weight,XGBoost_weight))


"""
Selecting product with confidence level above threshold.
Then combine products within the same order together
Write output to out.csv
"""

"""Threshold settings"""
light = pd.read_csv('lgbm_pred.csv')
xg = pd.read_csv('xgboost_pred.csv') #0.3749265

result = pd.DataFrame()
result['order_id'] = light['order_id']
result['product_id'] = light['product_id']
result['confidence'] = lightGBM_weight * light['confidence'] + XGBoost_weight * xg['confidence']

result = result[result['confidence'] >= threshold]
result = result.groupby('order_id')['product_id'].apply(list).reset_index()
result.columns = ['order_id', 'products']
result['products'] = result['products'].apply(lambda x: " ".join(str(num) for num in x))
submission = pd.read_csv(DIR + 'sample_submission.csv')
submission = submission.drop('products', axis=1)
submission = pd.merge(submission, result, on='order_id', how='left').fillna("None")
submission = submission.sort_values('order_id')
print("Writing output")
submission.to_csv('out.csv', index=False, mode='w+', quoting=csv.QUOTE_NONE)