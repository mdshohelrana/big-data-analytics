#%%

from pyspark.sql import SparkSession
from pyspark.sql import functions as F, types as T, Window

spark = SparkSession.builder.getOrCreate()

# %%

# load data/shopping_trends/shopping_trends.csv into a DataFrame
shopping_trends = spark.read.csv('data/shopping_trends/shopping_trends.csv', header=True)
shopping_updated = spark.read.csv('data/shopping_trends/shopping_trends_updated.csv', header=True)


# %%

shopping_trends.show()

# %%

shopping_updated.show()
# %%

shopping_all = shopping_trends.unionByName(
    shopping_updated, 
    allowMissingColumns=True
)

shopping_all.show()

# %%

set(shopping_trends.columns) ^ set(shopping_updated.columns)

# %%

shopping_trends.count(), shopping_updated.count(), shopping_all.count()
# %%

# these three filters do the same
(
    shopping_updated
    .filter(F.col("Gender") == "Male")
    .filter("Gender == 'Male'")
    .filter(shopping_updated["Gender"] == "Male")
    .show()
)

#%%

purchases_male = (
    shopping_trends
    .filter(F.col("Gender") == "Male")
)

purchases_female = (
    shopping_trends
    .filter(F.col("Gender") != "Male")
)


# %%

(
    purchases_male
    .groupby("category", "Gender")
    .agg(F.sum("Purchase Amount (USD)").alias("spending"))
    .show()
)



# %%
(
    purchases_female
    .groupby("category", "Gender")
    .agg(F.sum("Purchase Amount (USD)").alias("spending"))
    .show()
)
# %%

comparison_categories = (
    (
        purchases_male
        .groupby("category", "Gender")
        .agg(F.sum("Purchase Amount (USD)").alias("spending"))
        .withColumnRenamed("spending", "spending_male")
    )
    .join(
        (
            purchases_female
            .groupby("category", "Gender")
            .agg(F.sum("Purchase Amount (USD)").alias("spending"))
            .withColumnRenamed("spending", "spending_female")
        ),
        how="left",
        on="category",
    )
)

comparison_categories.show()

# %%

(
    comparison_categories
    .withColumn(
        "spending_difference",
        F.col("spending_male") - F.col("spending_female")
    )
    .show()
)

# %%

# intro to Window function

# load titanic dataset
titanic = spark.read.csv('data/titanic.csv', header=True, inferSchema=True)

titanic_with_surname = (
    titanic
    .withColumn(
        "Surname", 
        F.split(F.col("Name"), ",")[0]
    )
)

# %%
titanic_with_surname.show()

# %%

# let's filter dataset to have only the youngest member of each family

# create pyspark window that splits by Surname and orders by Age
window = (
    Window
    .partitionBy("Surname")
    .orderBy(F.col("Age").asc())
)

#%%

# apply window to titanic_with_surname
(
    titanic_with_surname
    .withColumn(
        "row_number",
        F.row_number().over(window)
    )
    # .filter(F.col("Surname") == "Palsson")
    .filter(F.col("row_number") == 1)
    .show()
)


# %%

# get fourth eldest in each family
(
    titanic_with_surname
    .withColumn(
        "row_number",
        F.row_number().over(window)
    )
    .filter(F.col("row_number") == 4)
    .show()
)
# %%

# UDFs - user defined function
# %%

# write an UDF that changes "PassengerID" to negative if "Survived" equals 1

def make_negative(id, survived) -> int:
    if survived == 1:
        return -id
    else:
        return id
    
make_negative_udf = F.udf(make_negative, T.IntegerType())

(
    titanic_with_surname
    .select(
        make_negative_udf(F.col("PassengerId"), F.col("Survived")).alias("new_id"),
        "*"
    )
    .show()
)

# %%


def return_an_array(id, survived):
    if survived == 1:
        return [-id, -id, -id]
    else:
        return [0, id]
    
return_an_array_udf = F.udf(
    return_an_array, 
    T.ArrayType(T.IntegerType())
)

(
    titanic_with_surname
    .select(
        return_an_array_udf(F.col("PassengerId"), F.col("Survived")).alias("new_array"),
        "*"
    )
    .show()
)
# %%

@F.udf(T.StructType([
    T.StructField("id", T.IntegerType()),
    T.StructField("values", T.ArrayType(T.IntegerType()))
]))
def return_an_array_nicely(id, survived):
    if survived == 1:
        return (3, [-id, -id, -id])
    else:
        return  (5, [0, id])

(
    titanic_with_surname
    .select(
        return_an_array_nicely(F.col("PassengerId"), F.col("Survived")).alias("new_array"),
    )
    .show()
)

#%%
(
    titanic_with_surname
    .select(
        return_an_array_nicely(F.col("PassengerId"), F.col("Survived")).alias("new_array"),
    )
    .printSchema()
)
# %%

(
    titanic_with_surname
    .select(
        return_an_array_nicely(F.col("PassengerId"), F.col("Survived")).alias("new_array"),
    )
    .select(
        "new_array",
        "new_array.id",
        "new_array.values"
    )
    .show()
)


# %%

(
    titanic_with_surname
    .select(
        return_an_array_nicely(F.col("PassengerId"), F.col("Survived")).alias("new_array"),
        "*",
    )
    .select(
        "new_array",
        F.explode("new_array.values").alias("exploded_values"),
        "*"
    )
    .show()
)
# %%
