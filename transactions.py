import streamlit as st
import sqlite3


def get_parties():
    connection = sqlite3.connect("agro_power.db")

    data = connection.execute("""
        SELECT id, name, party_type
        FROM parties
        ORDER BY name
    """).fetchall()

    connection.close()

    return data


def get_products():
    connection = sqlite3.connect("agro_power.db")

    data = connection.execute("""
        SELECT id, name, unit
        FROM products
        ORDER BY name
    """).fetchall()

    connection.close()

    return data


def save_transaction(
    transaction_date,
    permission_number,
    transaction_type,
    party_id,
    driver_name,
    car_number,
    responsible_person,
    items
):
    connection = sqlite3.connect("agro_power.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO transactions (
            transaction_date,
            permission_number,
            transaction_type,
            party_id,
            driver_name,
            car_number,
            responsible_person
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        transaction_date,
        permission_number,
        transaction_type,
        party_id,
        driver_name,
        car_number,
        responsible_person
    ))

    transaction_id = cursor.lastrowid

    for item in items:
        cursor.execute("""
            INSERT INTO transaction_items (
                transaction_id,
                product_id,
                quantity,
                price,
                value
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            transaction_id,
            item["product_id"],
            item["quantity"],
            item["price"],
            item["value"]
        ))

    connection.commit()
    connection.close()


def get_transactions(transaction_type):
    connection = sqlite3.connect("agro_power.db")

    data = connection.execute("""
        SELECT
            t.id,
            t.transaction_date,
            t.permission_number,
            p.name,
            t.driver_name,
            t.car_number,
            t.responsible_person,
            ti.id,
            pr.name,
            ti.quantity,
            ti.price,
            ti.value
        FROM transactions t
        JOIN parties p
            ON t.party_id = p.id
        JOIN transaction_items ti
            ON t.id = ti.transaction_id
        JOIN products pr
            ON ti.product_id = pr.id
        WHERE t.transaction_type = ?
        ORDER BY t.id DESC, ti.id ASC
    """, (transaction_type,)).fetchall()

    connection.close()

    return data
def delete_transaction(transaction_id):
    connection = sqlite3.connect("agro_power.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM transaction_items WHERE transaction_id = ?",
        (transaction_id,)
    )

    cursor.execute(
        "DELETE FROM transactions WHERE id = ?",
        (transaction_id,)
    )

    connection.commit()
    connection.close()

def show(transaction_type):

    st.header(f"{transaction_type} 📋")

    parties = get_parties()
    products = get_products()

    if not parties:
        st.warning("يجب تسجيل عميل أو مورد أولاً.")
        return

    if not products:
        st.warning("يجب تسجيل صنف أولاً.")
        return

    if "transaction_items" not in st.session_state:
        st.session_state.transaction_items = []

    party_names = [party[1] for party in parties]

    selected_party = st.selectbox(
        "العميل / المورد",
        party_names
    )

    permission_number = st.text_input(
        "رقم الإذن"
    )

    transaction_date = st.date_input(
        "التاريخ"
    )

    driver_name = st.text_input(
        "اسم السائق"
    )

    car_number = st.text_input(
        "رقم السيارة"
    )

    responsible_person = st.text_input(
        "اسم المسؤول"
    )

    st.divider()

    st.subheader("📦 إضافة صنف للإذن")

    product_names = [product[1] for product in products]

    selected_product = st.selectbox(
        "الصنف",
        product_names
    )

    selected_product_data = next(
        product
        for product in products
        if product[1] == selected_product
    )

    st.write(
        f"الوحدة: **{selected_product_data[2]}**"
    )

    quantity = st.number_input(
        "الكمية",
        min_value=0.0,
        step=1.0,
        key="item_quantity"
    )

    price = st.number_input(
        "السعر",
        min_value=0.0,
        step=0.01,
        key="item_price"
    )

    item_value = quantity * price

    st.write(
        f"قيمة الصنف: **{item_value:,.2f}**"
    )

    if st.button("➕ إضافة الصنف للإذن"):

        if quantity <= 0:
            st.error(
                "من فضلك أدخل كمية أكبر من صفر."
            )

        else:
            st.session_state.transaction_items.append({
                "product_id": selected_product_data[0],
                "product_name": selected_product_data[1],
                "unit": selected_product_data[2],
                "quantity": quantity,
                "price": price,
                "value": item_value
            })

            st.success(
                "تمت إضافة الصنف للإذن ✅"
            )

    st.divider()

    st.subheader("📋 أصناف الإذن الحالي")

    if st.session_state.transaction_items:

        total_value = 0

        for index, item in enumerate(
            st.session_state.transaction_items
        ):

            col1, col2 = st.columns([5, 1])

            with col1:
                st.write(
                    f"**{index + 1}. {item['product_name']}** | "
                    f"الوحدة: {item['unit']} | "
                    f"الكمية: {item['quantity']} | "
                    f"السعر: {item['price']:,.2f} | "
                    f"القيمة: {item['value']:,.2f}"
                )

            with col2:
                if st.button(
                    "🗑️ حذف",
                    key=f"delete_item_{index}"
                ):
                    st.session_state.transaction_items.pop(index)
                    st.rerun()

            total_value += item["value"]

        st.subheader(
            f"💰 إجمالي الإذن: {total_value:,.2f}"
        )

        if st.button("💾 حفظ الإذن بالكامل"):

            if permission_number.strip() == "":
                st.error(
                    "من فضلك أدخل رقم الإذن."
                )

            else:

                selected_party_id = next(
                    party[0]
                    for party in parties
                    if party[1] == selected_party
                )

                save_transaction(
                    transaction_date.strftime("%Y-%m-%d"),
                    permission_number,
                    transaction_type,
                    selected_party_id,
                    driver_name,
                    car_number,
                    responsible_person,
                    st.session_state.transaction_items
                )

                st.success(
                    "تم حفظ الإذن بالكامل بنجاح ✅"
                )

                st.session_state.transaction_items = []

    else:
        st.info(
            "لم تتم إضافة أي أصناف للإذن بعد."
        )

    st.divider()

    st.subheader("📋 الأذونات المسجلة")

    transactions = get_transactions(transaction_type)

    if transactions:

        for transaction in transactions:

            col1, col2 = st.columns([6, 1])

            with col1:
                st.write(
                    f"**إذن رقم {transaction[2]}** | "
                    f"التاريخ: {transaction[1]} | "
                    f"العميل/المورد: {transaction[3]} | "
                    f"السائق: {transaction[4]} | "
                    f"السيارة: {transaction[5]} | "
                    f"الصنف: {transaction[8]} | "
                    f"الكمية: {transaction[9]} | "
                    f"السعر: {transaction[10]:,.2f} | "
                    f"القيمة: {transaction[11]:,.2f}"
                )

            with col2:
                if st.button(
                    "🗑️ حذف",
                    key=f"delete_transaction_{transaction[0]}_{transaction[7]}"
                ):
                    delete_transaction(transaction[0])
                    st.success("تم حذف الإذن بنجاح ✅")
                    st.rerun()

    else:
        st.info(
            "لا توجد أذونات مسجلة."
        )