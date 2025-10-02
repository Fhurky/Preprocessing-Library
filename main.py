from fonk.Preprocess4data import Preprocessor
import os

os.system("clear")

data = Preprocessor(csv_file_path="./archive/furkan.csv")

data.preview(n=0) # n=0 for all    Not: Güzel çalışıyor

data.check_column(column_name="Result", cat_threshold_value=0.4, error_rate=0.05) # cat_threshold_value=n buradaki minimum kategori oranı Not: Gözden geçirilmesi gerek

