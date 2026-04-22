import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import re
from datetime import date
# DB connection
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="salesdb",
        user="postgres",
        password="AJV06",
        port="5432"
    )

# run_querry cmd:
def run_query(sql):
    conn=get_connection() # get connect to DB
    cur=conn.cursor()  # to get query get variable

    cur.execute(sql)  # run the query given
    result= cur.fetchone()[0] # fetch a single single row
    
    cur.close()
    conn.close()
    return result

# Create Session: Session Initialization

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "login"

if "form_id" not in st.session_state:
     st.session_state.form_id = 0

if "start_form" not in st.session_state:
    st.session_state.start_form = False



def login():
    st.sidebar.markdown(
    "<h2 style='color:red; font-family:Arial, font-align:left'>Sales Intelligence Hub</h2>",
    unsafe_allow_html=True
)
    st.title("Login 👤")
    user_name = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user= is_valid_login(user_name, password) #arugument
        if user:
          st.session_state.logged_in = True
          st.session_state.user = user
          st.rerun()   # 🔥 IMPORTANT
        else:
          st.error("Invalid credentials")
    

# Check login

def is_valid_login(username, password): # parameter
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s;",
        (username, password)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user   # shows the row (id,U_name,pwd.bid,role,email)
    
# Sidebar Functions:
def sidebar_fuc():
    
    user=st.session_state.get("user")
    if user is None:
          st.sidebar.warning("Invalid")
          return
    _,_,r_ad= get_user_info()
    role=user[4]
    branch_id=user[3]
    
    st.sidebar.markdown(
    "<h2 style='color:purple; font-family:Open Sans, font-align:left; font-style:italic;'>Welcome to Sales Hub📊</h2>",
    unsafe_allow_html=True
)
    if role == "Super Admin":   
        st.sidebar.subheader(f"Role: {role}")
    else:
        st.sidebar.subheader(f"Role: {role}")
        st.sidebar.write(f"Branch_ID: {branch_id}")
        st.sidebar.write(f"Branch_Name: {r_ad[1].title()}")

#role & branch of user:
def get_user_info():
    user = st.session_state.get("user")

    if user is None:
        return None, None
     
    username=user[1]
    r_ad=username.split("_")
    print (r_ad)     
    print (r_ad[0])         # r_ad[0]=admin , r_ad[1]= branch_name (in lower)
    role = user[4]
    branch_id = user[3]

    return role, branch_id, r_ad

# Read sales data: Disp sales for all branch
def fetch_sales_SA():
    conn =get_connection()
    role, branch_id, r_ad= get_user_info()

    if role == "Super Admin":
        query="SELECT * FROM customer_sales ORDER BY sale_id ASC"
        df=pd.read_sql(query, conn)
    elif r_ad[0].title() == "Admin":
        query="SELECT * FROM customer_sales WHERE branch_id = %s ORDER BY sale_id ASC"
        df= pd.read_sql(query, conn, params=(branch_id,))
    conn.close()
    return df

#Read Branch data:
def fetch_branch_SA():
    conn =get_connection()
    role, _,_= get_user_info()
    if role == "Super Admin":    
        query=" SELECT cs.*, b.branch_name FROM customer_sales cs JOIN branches b ON cs.branch_id = b.branch_id"
                
        df= pd.read_sql(query, conn)
    conn.close()
    return df


#Payment Details:
def fetch_payment_detail():
    conn =get_connection()
    role, branch_id,r_ad= get_user_info()
    if role.title() == "Super Admin":
        query=""" SELECT p.* FROM payment_splits p"""
        
        df= pd.read_sql(query, conn)
    elif r_ad[0].title() == "Admin":                                                  # admin
        query = """
        SELECT p.* 
        FROM payment_splits p
        JOIN customer_sales s ON p.sale_id = s.sale_id
        WHERE s.branch_id = %s
        """
        df = pd.read_sql(query, conn, params=(branch_id,))
    conn.close()
    return df

@st.dialog("✅ Sale Added Successfully!")
def my_dialog1(name,branch_na):
    st.write(f"HI, {name}!")
    st.write(f"WELCOME to {branch_na}")
    if st.button("Close"):
        st.rerun()
#Add Sale:
     
def add_sale():    
    conn =get_connection()
    role, branch_id, r_ad= get_user_info()
   
    st.title("Sale Form")
    with st.form(f"sales_form_{st.session_state.form_id}"):
            if role == "Super Admin":
                branch={
                        "Chennai":"1",
                        "Bangalore":"2",
                        "Hyderabad":"3",
                        "Delhi":"4",
                        "Mumbai":"5",
                        "Pune":"6",
                        "Kolkata":"7",
                        "Ahmedabad":"8"
                        }
                branch_name=st.selectbox("Select Branch:",list(branch.keys()))
                if st.form_submit_button("Get ID"):
                     branch_id=branch[branch_name]
                     st.success(f"Branch ID: {branch_id}")
                branch_id=branch[branch_name]
            else:
                branch_id=st.number_input("***Branch_ID:***", value= branch_id, disabled=True)
                st.text_input("***Branch_Name:***", value= r_ad[1], disabled=True)
                #branch_id=st.text_input(f"Enter Branch ID:{}") 
            date=st.date_input("***Enter Date 🗓️:***")
            name=st.text_input("***Enter Name:***")
            mobile_number=st.text_input("***Enter Mobile Number:***")
            product_name=st.selectbox("***Select Course 🎓:***",
        ["AI","BI","ML","BA","SQL","DA","FSD","DS"],
        index=0)
            gross_sales=st.number_input("***Enter Total Amount ₹:***")
            #received_amount=st.number_input("***Amount Paid ₹:***", value=0)
            status=st.selectbox("***Status 🗄️:***",["Open","Close"])            
            submitted=st.form_submit_button(label='Add Sale')
            if submitted:
                if name != name.title() or not re.fullmatch(r"^[6-9]\d{9}$", mobile_number):
                    st.error("Enter a valid details")
                else:
                    conn=get_connection()
                    cur=conn.cursor()
                    insert_query="""
                                INSERT INTO customer_sales(branch_id,date,name,mobile_number,product_name,gross_sales,status)
                                VALUES (%s,%s,%s,%s,%s,%s,%s)
                                """
                    cur.execute(insert_query,(branch_id,date,name,mobile_number,product_name,gross_sales,status))
                    conn.commit()
                    
                    my_dialog1(name,branch_name)
                    st.session_state.form_id += 1       
                    cur.close()
                    conn.close()
                   
# Dialog Box:
@st.dialog("PAYMENT SUCCESSFUL")
def my_dialog(p_method):
    # st.write(f"Amount Completed via {"p_method"} ")   
     st.markdown(
    f"""
    <div style="
        background-color:#f0f2f6;
        padding:15px;
        border-radius:10px;
        text-align:center;
    ">
        <h2 style="color:#2E86C1;">Amount Paid via {p_method} </h2>
        
    </div>
    """,
    unsafe_allow_html=True
)
     if st.button("close"):
          st.rerun()                   
                   
# Add Payment Details: 
def add_payment():                       
    conn=get_connection()
    cur=conn.cursor()
   
    role, branch_id, r_ad= get_user_info()
    
    st.title("Payment Form")
    with st.form(f"sales_form_{st.session_state.form_id}"):
        if role == "Super Admin":
            df_SA=pd.read_sql("SELECT branch_name FROM branches",conn)
            branch_n=st.selectbox("Select Branch Name:",df_SA["branch_name"])
        else:
            branch_id=st.number_input("***Branch_ID:***", value= branch_id, disabled=True)
            st.text_input("***Branch_Name:***", value= r_ad[1], disabled=True)
        sale_id= st.number_input("***Sale.ID:***",min_value=0,step=1)  
        pending =None
        sub_pen=st.form_submit_button("Check Pending Amount:")
        if sale_id and sub_pen:
            cur.execute("SELECT pending_amount FROM customer_sales WHERE sale_id=%s", (sale_id,))

            result = cur.fetchone()
            if result:
                pending = result[0]
                st.info(f"💰 Pending Amount: ₹{pending}")
            else:
                st.success("Payment Completed")
            
        payment_date= st.date_input("***Payment Date 🗓️:***")#,Value=date.today())
            #payment_date = date.today()  
        amount_paid= st.number_input("***Amount Paid ₹:***")
        payment_method = st.radio(
                 "Payment Mode:",
                ["Cash","Card","UPI"], 
                horizontal=True
                   )
        submit_p=st.form_submit_button("SUBMIT")
    if submit_p:
                #validate sale id
        cur.execute("SELECT * FROM customer_sales WHERE sale_id = %s", (sale_id,))
        exists = cur.fetchone()
        if not exists:
            st.error("❌ Invalid Sale ID! Not found in database.")
        else:
            insert_query="""
                    INSERT INTO payment_splits(sale_id,payment_date,amount_paid,payment_method)
                    VALUES (%s,%s,%s,%s)
                    """
            cur.execute(insert_query,(sale_id,payment_date,amount_paid,payment_method))
            conn.commit()
            
            my_dialog(payment_method)
            st.session_state.form_id += 1
           # st.rerun()
    cur.close()
    conn.close()

# Filter Function  
def dash_filter_SA():
    conn=get_connection()
    role, branch_id,r_ad=get_user_info()
    df=pd.read_sql(" SELECT cs.*, b.branch_name FROM customer_sales cs JOIN branches b ON cs.branch_id = b.branch_id ORDER BY sale_id  ASC", conn)
    df["date"] = pd.to_datetime(df["date"])
    st.header("Sales Data")
    #st.dataframe(df)
    col1, col2, col3 = st.columns(3)
    with col1:
        branch=st.selectbox("Branch", ["All"+ sorted(df["branch_name"].unique())])
    with col2:
        product=st.selectbox("Course", sorted(df["product_name"].unique()))
    with col3:
        status=st.selectbox("Status", df["status"].unique())

# date filter:
    col1, col2= st.columns(2)
    with col1:
        min_date= df["date"].min()
        from_date =st.date_input("Date From",min_date)
    with col2:
        max_date= df["date"].max()
        to_date=st.date_input("To",max_date)
   
    filtered_df = df.copy()

    if branch != "All":
         filtered_df = filtered_df[filtered_df["branch_name"] == branch]

    if product != "All":
        filtered_df = filtered_df[filtered_df["product_name"] == product]

    if status != "All":
        filtered_df = filtered_df[filtered_df["status"] == status]
    
    filtered_df=df[
        (df["branch_name"] == branch) &
        (df["product_name"] == product) &
        (df["status"]== status)&
        (df["date"]>=pd.to_datetime(from_date)) &
        (df["date"]<=pd.to_datetime(to_date)) 
    ]

# Slider:
    max_gross = int(filtered_df["gross_sales"].max())

    received_min = 0
    received_max = int(filtered_df["received_amount"].max())
    rec_min, rec_max = st.slider(
        " 💰 Received Amount",
        received_min,
        received_max,
        (received_min, received_max)
    )
     
    final_df = filtered_df[
        filtered_df["received_amount"].between(rec_min, rec_max)
    ]
    col1,col2,col3 = st.columns(3)
    with col1:
        st.metric("Gross", final_df["gross_sales"].sum())
    with col2:
        st.metric("Received", final_df["received_amount"].sum())
    with col3:
        st.metric("Pending", int(final_df["pending_amount"].sum()))
   
    st.dataframe(final_df)

#Dash--Performance 1:
def show_perf_SA():
        conn=get_connection()
        df_cust=pd.read_sql("SELECT product_name, COUNT(name) AS tot_cust FROM customer_sales GROUP BY product_name ORDER BY tot_cust DESC",conn)
        st.header("📈 Productwise Sale")
        fig= px.pie(df_cust,
                    names="product_name",
                    values="tot_cust",
                    hole=0.5
                    )
        fig.update_traces(textinfo="label+value")
        st.plotly_chart(fig,use_container_width=True)
        df_1=pd.read_sql(" SELECT cs.*, b.branch_name FROM customer_sales cs JOIN branches b ON cs.branch_id = b.branch_id ORDER BY sale_id  ASC", conn)
        tot_cust=df_1["name"].nunique()
        print(tot_cust)
        cust_per_branch=df_1.groupby("branch_name")["name"].nunique().reset_index()
        cust_per_branch.columns=["branch_name","tot_cust"]
        print(cust_per_branch)
# BAR CHART:
        st.header(" 📦 Branchwise Sale")
        fig_1=px.bar(
        cust_per_branch,
        x="branch_name", #what to disp in x
        y="tot_cust",    #what to disp in y
        text="tot_cust",  # what value to be disp on bar top
        color="branch_name" #give diff branch diff color
    )
        fig_1.update_traces(textposition="outside")
        st.plotly_chart(fig_1)


# Dash--Perf 2:
def show_perf_A():
    conn=get_connection()
    _, branch_id,_= get_user_info()
# PIE CHART:
    query="SELECT product_name, COUNT(name) AS tot_cust1 FROM customer_sales WHERE branch_id = %s GROUP BY product_name ORDER BY tot_cust1 DESC"
    df_cust = pd.read_sql(query, conn, params=(branch_id,))
    st.header("📈 Productwise Sale")
    
    fig= px.pie(df_cust,
                names= "product_name",
                values= "tot_cust1",
                )
    fig.update_traces(textinfo="label+value+percent")
    st.plotly_chart(fig,use_container_width=True)

def show_perf1_A():
    conn=get_connection()
    _, branch_id,_= get_user_info()
    query=" SELECT cs.*, b.branch_name FROM customer_sales cs JOIN branches b ON cs.branch_id = b.branch_id WHERE cs.branch_id = %s ORDER BY sale_id  ASC"
    df=pd.read_sql(query, conn, params=(branch_id,))
    df["date"]= pd.to_datetime(df["date"])
    df["month"]=df["date"].dt.to_period("M")
    monthly_sales=df.groupby(["month","product_name"])["gross_sales"].sum().reset_index()
    pivot_df = monthly_sales.pivot(index="month", columns="product_name", values="gross_sales")
    pivot_df.index = pivot_df.index.astype(str)
    st.title("Monthly Sales by Product")
    st.line_chart(pivot_df)

##### SQL QUERIES ####
def sql_qry():
    conn=get_connection()
    queries={
          "1. Customer Sales Record": "SELECT * FROM customer_sales",
          "2. Branches Record": "SELECT * FROM branches",
          "3. Payment Splits Record": "SELECT * FROM payment_splits",
          "4. Chennai Branch Record": "SELECT * FROM customer_sales WHERE branch_id=1 ORDER BY product_name ASC",
          "5. Total Gross Sales": "SELECT SUM(gross_sales) AS GROSS_AMOUNT FROM customer_sales",
          "6. Total Received Amount": "SELECT SUM(received_amount) AS RECEIVED_AMOUNT FROM customer_sales",
          "7. Total Pending Amount":  "SELECT SUM(pending_amount) AS PENDING_AMOUNT FROM customer_sales",
          "8. Average Gross Amount":"SELECT ROUND(AVG(gross_sales),2) AS AVERAGE_GROSS_AMT FROM customer_sales",
        #"9. Sales per Branch": "SELECT T2.branch_id AS Branch_ID,T2.branch_name AS Branch_Name,COUNT(T1.sale_id) AS Sales_Count FROM customer_sales T1 JOIN branches T2 ON T1.branch_id = T2.branch_id GROUP BY T2.branch_id,T2.branch_name order by T2.branch_id,T2.branch_name",
          "9. Complete Sales details with branch name":"SELECT cs.sale_id, b.branch_name, cs.date, cs.name, cs.product_name, cs.gross_sales, cs.received_amount,cs.pending_amount, cs.status FROM branches b INNER JOIN customer_sales cs ON b.branch_id = cs.branch_id", 
          "10. Sales Total Payment Details": "SELECT cs.sale_id,cs.product_name,SUM(p.amount_paid) AS Total_Amount_Paid FROM customer_sales cs JOIN payment_splits p ON cs.sale_id = p.sale_id GROUP BY cs.sale_id, cs.product_name ORDER BY cs.sale_id",
          "11. Total Gross Sale Branchwise": "SELECT b.branch_name, SUM(cs.gross_sales) AS total_gross FROM branches b JOIN customer_sales cs ON b.branch_id = cs.branch_id GROUP BY b.branch_name", 
          "12. Sales with Branch Admin Name": "SELECT b.branch_id AS Branch_Id, b.branch_name ,b.branch_admin_name, extract(month from cs.date) as Sale_Month, cs.product_name, cs.status,count(cs.sale_id) AS total_sales, sum(cs.gross_sales) AS Total_gross_sales, sum(cs.received_amount) as Total_Recieved_Amount,sum(cs.pending_amount) as Total_pending_amount FROM branches b INNER JOIN customer_sales cs ON b.branch_id = cs.branch_id group by b.branch_id, b.branch_name ,b.branch_admin_name, extract(month from cs.date), cs.product_name, cs.status order by b.branch_id",
          "13. Pending Sales(>5000)":"SELECT cs.sale_id,b.branch_name,cs.name,cs.pending_amount FROM customer_sales cs JOIN branches b ON cs.branch_id=b.branch_id WHERE pending_amount > 5000 GROUP BY cs.sale_id,b.branch_name,cs.name, cs.pending_amount ORDER BY b.branch_name ASC",
          "14. Highest Gross Sale": "SELECT b.branch_name, SUM(cs.gross_sales) AS Total_Gross FROM branches b JOIN customer_sales cs ON cs.branch_id = b.branch_id GROUP BY b.branch_name ORDER BY Total_Gross DESC LIMIT 1",
          "15. Payment Methodwise Total":"SELECT payment_method,COUNT(sale_id) AS Total_Count FROM payment_splits GROUP BY payment_method"
         }
    st.title("SQL QUERIES")
    select_qry=st.selectbox("Select Report",list(queries.keys()))
    df=pd.read_sql(queries[select_qry],conn)
    st.dataframe(df)


# Main Dashboard:
# ______________    
    
def dashboard():
    st.title("Dashboard")
# 1:get role:
    role, branch_id, r_ad=get_user_info()
    if role == "Super Admin":
        st.markdown(f"<h3 style='color:green;'>Welcome,{role.title()}👑 </h3>", unsafe_allow_html=True)
    elif role == "Admin":
        print (r_ad[0])
        st.markdown(f"<h3 style='color:green;'>Welcome,{r_ad[0].title()}👥 </h3>", unsafe_allow_html=True)
        st.markdown("___________")
    
    sidebar_fuc()
   
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user=None
        st.session_state.page = "login"
        st.rerun()   

# Selection of Access:
#2: chec with role:
    if role and role.title() == "Super Admin":
        access_to= ["Dashboard","Add Sale","Add Payment","All Sales Data","Branch Sales","Payment Details","SQL Queries"]
    else:
        access_to=["Dashboard","Add Sale","Add Payment","Payment Details"]    
#3: access_to selectbox:
    access_to = st.sidebar.selectbox("Select Access ",access_to,index =0)
    
#### SUPER ADMIN ######

    if access_to == "Dashboard":
        if role and role.title() == "Super Admin": # title means case sensitive
            dash_filter_SA()
            show_perf_SA()
            
        elif r_ad[0].title() == "Admin": 
            df = fetch_sales_SA()
            st.subheader("All Sales Data")
            st.dataframe(df)
            show_perf_A()
            show_perf1_A()
    elif access_to=="Add Sale":                 
            add_sale()   
    elif access_to== "Add Payment":
            add_payment()
    elif access_to == "All Sales Data":
            df = fetch_sales_SA()
            st.subheader("All Sales Data")
            st.dataframe(df)

    elif access_to == "Branch Sales":
           
                df= fetch_branch_SA()
                st.header(" 🧾 Branch Sales Data")
                for branch_id, data in df.groupby("branch_id"):
                    branch_name = data["branch_name"].iloc[0]

                    st.markdown(f"### 🏢 {branch_name} (ID: {branch_id})")
                    st.dataframe(data)
         
    elif access_to == "Payment Details": 

                df= fetch_payment_detail()
                st.subheader("💵 Payment Data")
                st.dataframe(df)
            
    elif access_to == "SQL Queries":
         sql_qry()
                               
# MAIN ROUTER (THIS IS WHAT YOU ARE MISSING)
if st.session_state.logged_in:
    dashboard()
else:
    #if st.session_state.page == "login":
       login()


    

