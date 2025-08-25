import streamlit as st
import time
import numpy as np
from scrape import scrape_it,begin_upload,data_prep,print_text
st.set_page_config(page_title="Twitter scrapper", layout="wide")

def render_page():
    st.title(":blue[*Twitter*] Scrapper")
    st.markdown("**T**his is a simple Twitter scrapper to get data from twitter profiles and tweets using :blue[selenium] and :blue[webdriver manager].")
    user_inp = st.text_input("Search :",placeholder="#Tags, @usernames,...", key="search_input")
    if user_inp:
        if user_inp[0]=='#':
            cols1,cols2,cols3 = st.columns(3)
            with cols1:
                from_date = st.date_input("From :")
            with cols2:
                to_date = st.date_input('To :')
            with cols3:
                tweets = st.number_input("tweets range :",min_value=10,max_value=100)
            if user_inp and from_date and to_date and tweets:
                    if from_date == to_date:
                        st.markdown(":orange[The date difference should be atleast one day]")
                    else:
                        if st.button("start scrapping",use_container_width=True,):
                            col_num = [0.7,0.3,0.3]
                            c1,c2,c3 = st.columns(col_num)
                            with st.spinner("scrapping started...",show_time=True):
                                start = time.time()
                                mt,est = scrape_it(test=user_inp,since=from_date,until=to_date,tweet_range=tweets)
                                st.session_state["main_tweets"]=mt
                                st.session_state["est_time"] = est
                                st.session_state["scrape_done"] = True
                                end = time.time()
                                if st.session_state["scrape_done"]:
                                    csv_data = data_prep(csv=True)
                                    json_data = data_prep(csv=False)
                                    with c1:
                                        st.button("upload to Database",on_click=begin_upload,use_container_width=True,help="upload the data to the monogoDB database")
                                    with c2:
                                        if csv_data:
                                            st.download_button("download .CSV",data=csv_data,file_name="tweets_data.csv",mime="text/csv",key="csv_download_button"+str(np.random.rand()),use_container_width=True,help="download csv file")
                                            # a = [[print_text(username=i[0],tweet_text=i[2],like=i[3],retweet=i[4],reply=i[5],date=i[6]) for i in list(val.values())] for val in st.session_state["main_tweets"]]
                                        else:
                                            st.write("no csv data found!")
                                    with c3:
                                        if json_data:
                                            st.download_button("download .JSON",data=json_data,file_name="tweets_data.json",mime="application/json",key="json_download_button"+str(np.random.rand()),use_container_width=True,help="download json file")
                                        else:
                                            st.write("No json data found!")
                                if est > (end-start): st.markdown(f"*Execution time* : :green[{end-start:.2f}] *seconds*")
                                elif not (est+5 < (end-start)): st.markdown(f"*Execution time* : :orange[{end-start:.2f}] *seconds*")
                                else: st.markdown(f"*Execution time* : :red[{end-start:.2f}] *seconds*")
                                # st.markdown("please wait, this may take a while...")

        else:
            if st.button("start scrapping ...",use_container_width=True):
                with st.spinner("started scraping...",show_time=True):
                    start = time.time()
                    est = scrape_it(test=user_inp)
                    end = time.time()
                    if est > (end-start): st.markdown(f"*Execution time* : :green[{end-start:.2f}] *seconds*")
                    elif not (est+5 < (end-start)): st.markdown(f"*Execution time* : :orange[{end-start:.2f}] *seconds*")
                    else: st.markdown(f"*Execution time* : :red[{end-start:.2f}] *seconds*")
    


if __name__ == "__main__":
    render_page()