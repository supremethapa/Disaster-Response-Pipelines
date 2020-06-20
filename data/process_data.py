import sys
import pandas as pd
from sqlalchemy import create_engine


def load_data(messages_filepath, categories_filepath):
    # loading messages dataset
    messages = pd.read_csv(messages_filepath)
    # loading categories dataset
    categories = pd.read_csv(categories_filepath)
    #merging datasets
    df = messages.merge(categories, on='id', how='inner')

    return df


def clean_data(df):
    # 1.spliting the values in the `categories` column on the `;` character so that each value becomes a separate column
    # creating a dataframe of the 36 individual category columns
    categories = df.categories.str.split(';', expand=True)
    # selecting the first row of the categories dataframe to create column names for the categories data
    row = categories.iloc[0]
    # extracting a list of new column names for categories.
    category_colnames = row.apply(lambda x: x[:-2])
    # renaming the columns of `categories` with new column names
    categories.columns = category_colnames
    # 2.converting category values to just numbers 0 or 1.
    # iterating through the category columns in df to keep only the last character of each string (the 1 or 0). For example, `related-0` becomes `0`, `related-1` becomes `1`. Convert the string to a numeric value.
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].str[-1]
        # convert column from string to numeric
        categories[column] = categories[column].astype(int)
    categories.head()
    # 3.replacing `categories` column in `df` with new category columns.
    # droping the original categories column from `df` dataframe since it is no longer needed
    df.drop('categories', axis=1, inplace=True)
    # concatenating the original dataframe with the new `categories` dataframe
    df = pd.concat([df, categories], axis=1)
    # 4.removing duplicates
    # droping the duplicates
    df.drop_duplicates(inplace=True)
    #droping rows with non 1 and 0 values in `related`
    df.drop(df.query('related != "0" and related != "1"').index, axis=0, inplace=True)

    return df


def save_data(df, database_filename):
    # saving the clean dataset into an sqlite database.
    engine = create_engine('sqlite:///DisasterResponse.db')
    df.to_sql('messages', engine, index=False)


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()