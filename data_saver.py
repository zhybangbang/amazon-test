import os
import time
import re
import pandas as pd
from logger import logger


class DataSaver:
    @staticmethod
    def save_to_excel(products, category_name):
        """保存商品信息到Excel文件"""
        try:
            if not products:
                logger.warning("No products to save")
                return

            # 准备数据
            safe_category_name = re.sub(r'[<>:"/\\|?*]', '_', category_name)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f'{safe_category_name}_bestsellers_{timestamp}.xlsx'

            # 创建DataFrame
            df = pd.DataFrame([
                {
                    'Rank': i + 1,
                    'Title': p['title'],
                    'Price': p['price'],
                    'Rating': p['rating'],
                    'Review Count': p['review_count'],
                    'ASIN': p['asin'],
                    'Description': p['description']
                }
                for i, p in enumerate(products)
            ])

            # 尝试保存文件
            DataSaver._try_save_file(df, filename)

        except Exception as e:
            logger.error(f"Error saving to Excel: {str(e)}")
            DataSaver._save_as_csv_backup(df, safe_category_name, timestamp)

    @staticmethod
    def _try_save_file(df, filename):
        """尝试在不同位置保存文件"""
        possible_dirs = [
            '.',
            os.path.expanduser('~'),
            os.path.join(os.path.expanduser('~'), 'Documents'),
            os.getenv('TEMP', os.path.expanduser('~'))
        ]

        for save_dir in possible_dirs:
            try:
                full_path = os.path.join(save_dir, filename)
                DataSaver._save_with_formatting(df, full_path)
                logger.info(f"Successfully saved to {full_path}")
                return
            except Exception as e:
                logger.warning(f"Error saving to {save_dir}: {str(e)}")
                continue

        raise Exception("Unable to save file in any of the attempted locations")

    @staticmethod
    def _save_with_formatting(df, full_path):
        """保存Excel文件并设置格式"""
        with pd.ExcelWriter(full_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Bestsellers')
            worksheet = writer.sheets['Bestsellers']

            # 自动调整列宽
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                )
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)

    @staticmethod
    def _save_as_csv_backup(df, category_name, timestamp):
        """作为备份保存为CSV文件"""
        try:
            csv_filename = f'{category_name}_bestsellers_{timestamp}.csv'
            csv_path = os.path.join(os.getenv('TEMP', '.'), csv_filename)
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            logger.info(f"Saved data as CSV instead at: {csv_path}")
        except Exception as csv_error:
            logger.error(f"Failed to save as CSV as well: {str(csv_error)}")
