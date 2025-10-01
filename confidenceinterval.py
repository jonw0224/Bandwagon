import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Generate some sample data
np.random.seed(42) # for reproducibility
x = np.linspace(0, 10, 50)
y = 2 * x + 1 + np.random.normal(0, 2, 50) # Linear relationship with some noise

# 2. Create the regression plot with a 95% confidence interval
plt.figure(figsize=(8, 6))
sns.regplot(x=x, y=y, ci=95, scatter_kws={'alpha':0.6}, line_kws={'color':'red'})

# 3. Customize the plot (optional)
plt.title('Linear Trend Line with 95% Confidence Interval')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.grid(True, linestyle='--', alpha=0.7)
plt.show()
