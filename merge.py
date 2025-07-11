import pandas as pd

df1 = pd.read_csv("sns_posts_cleaned.csv", encoding="utf-8-sig")
df2 = pd.read_csv("sns_posts_cleaned2.csv", encoding="utf-8-sig")

merged_df = pd.concat([df1, df2], ignore_index=True)

merged_df.to_csv("merged.csv", index=False, encoding="utf-8-sig")
print("병합 완료")
