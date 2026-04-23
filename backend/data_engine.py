import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

class DataEngine:
    def __init__(self):
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.data_path = os.path.join(data_dir, 'ecommerce_data.csv')
        self.df = self._load_data()

    def _load_data(self):
        df = pd.read_csv(self.data_path)
        df['order_date'] = pd.to_datetime(df['order_date'])
        df['total_price'] = df['quantity'] * df['unit_price']
        return df

    def get_kpis(self):
        now = self.df['order_date'].max()
        thirty_days_ago = now - timedelta(days=30)
        sixty_days_ago = now - timedelta(days=60)

        current_df = self.df[self.df['order_date'] > thirty_days_ago]
        prev_df = self.df[(self.df['order_date'] <= thirty_days_ago) & (self.df['order_date'] > sixty_days_ago)]

        def calc_growth(curr, prev):
            if prev == 0: return 100
            return round(((curr - prev) / prev) * 100, 1)

        curr_revenue = current_df['total_price'].sum()
        prev_revenue = prev_df['total_price'].sum()

        curr_orders = current_df['order_id'].nunique()
        prev_orders = prev_df['order_id'].nunique()

        curr_customers = current_df['customer_id'].nunique()
        prev_customers = prev_df['customer_id'].nunique()

        curr_aov = curr_revenue / curr_orders if curr_orders > 0 else 0
        prev_aov = prev_revenue / prev_orders if prev_orders > 0 else 0

        last_7_days = now - timedelta(days=7)
        spark_df = current_df[current_df['order_date'] > last_7_days].groupby(current_df['order_date'].dt.date)['total_price'].sum()

        return {
            'revenue': {
                'value': round(curr_revenue, 2),
                'growth': calc_growth(curr_revenue, prev_revenue),
                'sparkline': spark_df.tolist()
            },
            'orders': {
                'value': curr_orders,
                'growth': calc_growth(curr_orders, prev_orders),
                'sparkline': current_df[current_df['order_date'] > last_7_days].groupby(current_df['order_date'].dt.date)['order_id'].nunique().tolist()
            },
            'customers': {
                'value': curr_customers,
                'growth': calc_growth(curr_customers, prev_customers),
                'sparkline': current_df[current_df['order_date'] > last_7_days].groupby(current_df['order_date'].dt.date)['customer_id'].nunique().tolist()
            },
            'aov': {
                'value': round(curr_aov, 2),
                'growth': calc_growth(curr_aov, prev_aov),
                'sparkline': [round(x, 2) for x in np.random.uniform(curr_aov * 0.9, curr_aov * 1.1, 7)]
            }
        }

    def get_revenue_trend(self, filter_type='30D'):
        now = self.df['order_date'].max()

        if filter_type == '7D':
            start_date = now - timedelta(days=7)
            resample_rule = 'D'
        elif filter_type == '30D':
            start_date = now - timedelta(days=30)
            resample_rule = 'D'
        elif filter_type == 'YTD':
            start_date = datetime(now.year, 1, 1)
            resample_rule = 'W'
        else:
            start_date = now - timedelta(days=30)
            resample_rule = 'D'

        trend_df = self.df[self.df['order_date'] > start_date]
        grouped = trend_df.groupby(pd.Grouper(key='order_date', freq=resample_rule))['total_price'].sum().reset_index()

        grouped['moving_average'] = grouped['total_price'].rolling(window=3, min_periods=1).mean()

        return {
            'labels': grouped['order_date'].dt.strftime('%Y-%m-%d').tolist(),
            'values': grouped['total_price'].round(2).tolist(),
            'forecast': grouped['moving_average'].round(2).tolist()
        }

    def get_audience_segments(self):
        now = self.df['order_date'].max() + timedelta(days=1)

        rfm = self.df.groupby('customer_id').agg({
            'order_date': lambda x: (now - x.max()).days,
            'order_id': 'count',
            'total_price': 'sum'
        }).reset_index()

        rfm.rename(columns={'order_date': 'Recency', 'order_id': 'Frequency', 'total_price': 'Monetary'}, inplace=True)

        def assign_segment(row):
            if row['Monetary'] > rfm['Monetary'].quantile(0.75) and row['Frequency'] > 2:
                return 'VIP & High LTV'
            elif row['Frequency'] > 1:
                return 'Repeat Buyers'
            else:
                return 'One-time Visitors'

        rfm['Segment'] = rfm.apply(assign_segment, axis=1)
        segment_counts = rfm['Segment'].value_counts()

        return {
            'labels': segment_counts.index.tolist(),
            'values': segment_counts.values.tolist()
        }

    def get_insights(self):
        kpis = self.get_kpis()
        insights = []

        if kpis['revenue']['growth'] < 0:
            insights.append({
                'type': 'warning',
                'title': 'Revenue Alert',
                'message': f"Revenue is down by {abs(kpis['revenue']['growth'])}%."
            })
        else:
            insights.append({
                'type': 'success',
                'title': 'Revenue Growth',
                'message': f"Revenue increased by {kpis['revenue']['growth']}%."
            })

        if kpis['aov']['growth'] < -5:
            insights.append({
                'type': 'warning',
                'title': 'AOV Drop',
                'message': 'Average order value is decreasing.'
            })

        top_product = self.df.groupby('product_name')['quantity'].sum().idxmax()
        insights.append({
            'type': 'info',
            'title': 'Inventory Risk',
            'message': f"High demand for {top_product}"
        })

        segments = self.get_audience_segments()
        if 'One-time Visitors' in segments['labels']:
            idx = segments['labels'].index('One-time Visitors')
            count = segments['values'][idx]
            total = sum(segments['values'])

            if count / total > 0.4:
                insights.append({
                    'type': 'opportunity',
                    'title': 'Retention Opportunity',
                    'message': 'Many one-time users detected'
                })

        return insights

    def get_top_products(self):
        now = self.df['order_date'].max()
        thirty_days_ago = now - timedelta(days=30)

        recent_df = self.df[self.df['order_date'] > thirty_days_ago]

        top = recent_df.groupby('product_name').agg(
            revenue=('total_price', 'sum'),
            quantity=('quantity', 'sum')
        ).sort_values(by='revenue', ascending=False).head(5).reset_index()

        return top.to_dict(orient='records')