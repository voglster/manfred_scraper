from selenium import webdriver
import pandas as pd
import selenium
from gspread_pandas import Spread
from loguru import logger


def get_header(frame):
    return frame.iloc[2]


def clean_page_df(frame):
    cleaned_frame = frame.iloc[3:-2]
    cleaned_frame.columns = get_header(frame)
    return cleaned_frame[[c for c in cleaned_frame.columns if str(c) != "nan"]]


def get_housing_df():
    driver = webdriver.PhantomJS()
    driver.get("http://www.treasurer.tulsacounty.org/trcommsale/")

    df = pd.read_html(driver.page_source)[0]
    df = clean_page_df(df)

    for i in range(2, 999):
        logger.debug(f"Doing page {i}")
        link_href = f"javascript:__doPostBack('GridView1','Page${i}')"
        try:
            driver.find_element_by_xpath(f'//a[@href="{link_href}"]').click()
        except selenium.common.exceptions.NoSuchElementException:
            logger.debug(f"Errored on page {i}")
            break
        new_df = pd.read_html(driver.page_source)[0]
        new_df = clean_page_df(new_df)
        df = df.append(new_df, ignore_index=True)
    return df


df = get_housing_df()

spread = Spread('james.vogel@capspire.com', 'Manfred Scraper')

spread.df_to_sheet(df, index=False, sheet='Housing', start='A1', replace=True)
