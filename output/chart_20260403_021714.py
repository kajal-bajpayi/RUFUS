
import matplotlib.pyplot as plt
import json

data = json.loads('{"columns": ["Runtime Error Category", "Count"], "rows": [["MESSAGE_TYPE_X", 45], ["DBIF_RSQL_SQL_ERROR", 30], ["TSV_TNEW_PAGE_ALLOC_FAILED", 25], ["UNCAUGHT_EXCEPTION", 20], ["CX_SY_DYN_CALL_ILLEGAL_TYPE", 15], ["ITAB_DUPLICATE_KEY", 10], ["TIME_OUT", 8], ["SYNTAX_ERROR", 7], ["CONVT_NO_NUMBER", 5], ["DATA_OFFSET_LENGTH_TOO_LARGE", 5]]}')

categories = [row[0] for row in data["rows"]]
counts = [row[1] for row in data["rows"]]

plt.style.use('seaborn-v0_8-darkgrid') # Professional styling

fig, ax = plt.subplots(figsize=(12, 7))

ax.bar(categories, counts, color='#1f77b4') # A nice blue color

ax.set_xlabel('ABAP Runtime Error Category', fontsize=12)
ax.set_ylabel('Number of Occurrences', fontsize=12)
ax.set_title('Most Common ABAP Short Dumps (Hypothetical Data)', fontsize=14, fontweight='bold')

plt.xticks(rotation=45, ha='right', fontsize=10) # Rotate labels for readability
plt.yticks(fontsize=10)

plt.tight_layout() # Adjust layout to prevent labels from overlapping
plt.savefig('C:/Users/kajal.bajpayi/Downloads/AI Agnet/output/common_abap_dumps.png')

print("Chart 'C:/Users/kajal.bajpayi/Downloads/AI Agnet/output/common_abap_dumps.png' generated successfully.")
