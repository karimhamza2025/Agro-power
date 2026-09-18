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


def add_payment(
    payment_date,
    party_id,
    payment_type,
    amount,
    notes
):
    connection = sqlite3.connect("agro_power.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO payments (
            payment_date,
            party_id,
            payment_type,
            amount,
            notes
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        payment_date,
        party_id,
        payment_type,
        amount,
        notes
    ))

    connection.commit()
    connection.close()


def get_payments():
    connection = sqlite3.connect("agro_power.db")

    data = connection.execute("""
        SELECT
            payments.id,
            payments.payment_date,
            parties.name,
            payments.payment_type,
            payments.amount,
            payments.notes
        FROM payments
        JOIN parties
            ON payments.party_id = parties.id
        ORDER BY payments.id DESC
    """).fetchall()

    connection.close()

    return data
def delete_payment(payment_id):
    connection = sqlite3.connect("agro_power.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM payments WHERE id = ?",
        (payment_id,)
    )

    connection.commit()
    connection.close()

def show():

    st.header("💰 الواردات والمدفوعات")

    parties = get_parties()

    if not parties:
        st.warning(
            "يجب تسجيل عميل أو مورد أولاً."
        )
        return

    st.subheader("💵 تسجيل حركة مالية")

    party_names = [
        party[1]
        for party in parties
    ]

    selected_party = st.selectbox(
        "العميل / المورد",
        party_names
    )

    payment_type = st.selectbox(
        "نوع الحركة",
        [
            "وارد",
            "مدفوع"
        ]
    )

    payment_date = st.date_input(
        "التاريخ"
    )

    amount = st.number_input(
        "المبلغ",
        min_value=0.0,
        step=0.01
    )

    notes = st.text_area(
        "ملاحظات"
    )

    if st.button("💾 حفظ الحركة"):

        if amount <= 0:
            st.error(
                "من فضلك أدخل مبلغ أكبر من صفر."
            )

        else:

            selected_party_id = next(
                party[0]
                for party in parties
                if party[1] == selected_party
            )

            add_payment(
                payment_date.strftime("%Y-%m-%d"),
                selected_party_id,
                payment_type,
                amount,
                notes
            )

            st.success(
                "تم حفظ الحركة المالية بنجاح ✅"
            )

    st.divider()

    st.subheader("📋 الحركات المالية المسجلة")

    payments = get_payments()

    if payments:

        for payment in payments:

            col1, col2 = st.columns([6, 1])

            with col1:
                st.write(
                    f"**{payment[1]}** | "
                    f"**{payment[2]}** | "
                    f"{payment[3]} | "
                    f"المبلغ: **{payment[4]:,.2f}** | "
                    f"{payment[5]}"
                )

            with col2:
                if st.button(
                    "🗑️ حذف",
                    key=f"delete_payment_{payment[0]}"
                ):
                    delete_payment(payment[0])
                    st.success("تم حذف الحركة المالية ✅")
                    st.rerun()

    else:
        st.info(
            "لا توجد حركات مالية مسجلة."
        )