def generate_insights(df):

    insights = []
    recommendations = []

    numeric_cols = df.select_dtypes(include='number').columns

    total_missing = df.isnull().sum().sum()

    # Missing values
    if total_missing > 0:
        insights.append(
            f"The dataset contains {total_missing} missing values."
        )

        recommendations.append(
            "Consider cleaning or filling missing values."
        )

    # Numeric analysis
    for col in numeric_cols:

        average = df[col].mean()

        max_value = df[col].max()

        if average > 100:
            insights.append(
                f"{col} has relatively high average values."
            )

        if max_value > 1000:
            insights.append(
                f"{col} contains unusually high maximum values."
            )

            recommendations.append(
                f"Review outliers in {col}."
            )

    return insights, recommendations