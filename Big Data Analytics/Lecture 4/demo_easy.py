#%%

from pyspark.sql import SparkSession
from pyspark.sql import functions as F, types as T

spark = SparkSession.builder.getOrCreate()
# %%
from datetime import datetime, date

schema = 'col1 long, value double, string_col string, date_col date, col_end timestamp'

# make same schema but using pyspark types
schema_same_but_complicatedly_written = T.StructType([
    T.StructField("col1", T.LongType(), True),
    T.StructField("value", T.DoubleType(), True),
    T.StructField("string_col", T.StringType(), True),
    T.StructField("date_col", T.DateType(), True),
    T.StructField("col_end", T.TimestampType(), True),
])


df = spark.createDataFrame([
    (1, 2., 'string1', date(2000, 1, 1), datetime(2000, 1, 1, 12, 0)),
    (2, 3., 'string2', date(2000, 2, 1), datetime(2000, 1, 2, 12, 0)),
    (3, 4., 'string3', date(2000, 3, 1), datetime(2000, 1, 3, 12, 0))
], schema=schema)
# %%

df.show()
# %%
df.show(1)
# %%
spark.conf.set('spark.sql.repl.eagerEval.enabled', True)
df
# %%

titanic = spark.read.csv('data/titanic.csv', header=True)
# %%


titanic = (
    spark
    .read
    .csv('data/titanic.csv', header=True)
    .select(
        "PassengerId", 
        "Survived", 
        "Name", 
        "Age", 
        F.col("Fare").cast("float"),
    )
)

titanic.show()
# %%

titanic.printSchema()
# %%

titanic.describe().show()
# %%
titanic.toPandas()
# %%

# make Surname column by taking the first part of Name column before comma
titanic_with_surname = (
    titanic
    .withColumn(
        "Surname", 
        F.split(F.col("Name"), ",")[0]
    )
)

titanic_with_surname.show()


#%%

# print surname=Palsson
titanic_with_surname.filter(F.col("Surname") == "Palsson").show()

# %%

(
    titanic_with_surname
    .filter(F.col("Surname") == "Palsson")

    .groupby("Surname")
    .agg(
        F.count("*").alias("Family size"),
        F.sum("Fare").alias("Total fare"),
    )  # aggregate

    .show()
)

# %%
titanic_with_surname.filter(
    (F.col("Surname") == "Palsson")
    & (F.col("Age") > 18)
).show()
# %%

# show computational graph for titanic_with_surname
titanic_with_surname.explain()
# %%

(
    titanic_with_surname
    .write.format("csv")
    .mode("overwrite")
    .option("header", "true")
    .save("data/titanic_with_surname.csv")
)


# %%

(
    titanic_with_surname
    .write.format("parquet")
    .mode("overwrite")
    .save("data/titanic_with_surname.parquet")
)

#%%

(
    titanic_with_surname
    .write.format("json")
    .mode("overwrite")
    .save("data/titanic_with_surname.json")
)

# %%

(
    spark
    .read
    .format("parquet")
    .load("data/titanic_with_surname.parquet")
    .show()
)
# %%

# read back JSON file into DataFrame and ignore the errors
(
    spark
    .read
    .format("json")
    .option("mode", "DROPMALFORMED")
    .load("data/titanic_with_surname.json")
    .show()
)

#%%

titanic_with_surname.createOrReplaceTempView("titanic_but_in_sql")

# %%

    # .groupby("Surname")
    # .agg(
    #     F.count("*").alias("Family size"),
    #     F.sum("Fare").alias("Total fare"),
    # )  # aggregate


spark.sql(
    """
    CREATE OR REPLACE TEMP VIEW titanic_out_of_sql AS
    SELECT 
        Surname, 
        COUNT(*) as Family_size, 
        SUM(Fare) as Total_fare
    FROM titanic_but_in_sql
    WHERE Surname = 'Palsson'
    GROUP BY Surname
    """
)

# %%

spark.table("titanic_out_of_sql").show()

# %%

(
    titanic
    .filter("Age > 18")
    .select(
        "*",
        # count number of commas in Name using SQL
        F.expr("size(split(Name, ',')) - 1").alias("Commas_in_name"),
        F.expr("PassengerId + 1").alias("PassengerId_plus_one"),
    )
    .show()
)


# %%
