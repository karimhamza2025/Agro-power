import streamlit as st
import database
import parties
import products
import transactions
import payments
import reports


st.set_page_config(
    page_title="Agro Power",
    page_icon="🚢",
    layout="wide"
)


st.sidebar.title("🚢 AGRO POWER")


menu = st.sidebar.radio(
    "القائمة الرئيسية",
    [
        "📊 الرئيسية",
        "📥 الوارد",
        "📤 الصادر",
        "👥 العملاء والموردين",
        "📦 الأصناف",
        "💰 الواردات والمدفوعات",
        "📋 التقارير",
        "⚙️ الإعدادات"
    ]
)


if menu == "👥 العملاء والموردين":

    parties.show()


elif menu == "📦 الأصناف":

    products.show()


elif menu == "📥 الوارد":

    transactions.show("📥 الوارد")


elif menu == "📤 الصادر":

    transactions.show("📤 الصادر")


elif menu == "💰 الواردات والمدفوعات":

    payments.show()


elif menu == "📋 التقارير":

    reports.show()


else:

    st.title("🚢 Agro Power")

    st.write(
        f"أنت الآن في: **{menu}**"
    )