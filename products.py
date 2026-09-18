import streamlit as st
import sqlite3


def add_product(name, unit, notes):
    connection = sqlite3.connect("agro_power.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO products (name, unit, notes)
        VALUES (?, ?, ?)
    """, (name, unit, notes))

    connection.commit()
    connection.close()


def get_products():
    connection = sqlite3.connect("agro_power.db")

    data = connection.execute("""
        SELECT id, name, unit, notes
        FROM products
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    return data


def show():
    st.header("📦 الأصناف")

    with st.form("product_form"):
        name = st.text_input("اسم الصنف")
        unit = st.text_input("الوحدة")
        notes = st.text_area("ملاحظات")

        submitted = st.form_submit_button("💾 حفظ")

        if submitted:
            if name.strip() == "":
                st.error("من فضلك أدخل اسم الصنف.")
            elif unit.strip() == "":
                st.error("من فضلك أدخل الوحدة.")
            else:
                add_product(name, unit, notes)
                st.success("تم حفظ الصنف بنجاح ✅")

    st.divider()

    st.subheader("📋 الأصناف المسجلة")

    products = get_products()

    if products:
        for product in products:
            st.write(
                f"**{product[1]}** | الوحدة: {product[2]} | "
                f"{product[3]}"
            )
    else:
        st.info("لا توجد أصناف مسجلة.")