import streamlit as st
import pandas as pd
import plotly.express as px


def main():
    # set parameter files
    parm_file = './parms.xlsx'

    # form the UI page & sidebar
    st.set_page_config(
        page_title="Zoo",
        page_icon=":tiger:",
        layout="centered",
        initial_sidebar_state="expanded",
    )

    # Code to remove 'hamburger' menu & 'Made with Streamlit' footer:
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.title("*Home Zoo Assessor*")

    # Collect all User Inputs #########################################################################################
    st.sidebar.title(":pencil: Input Details")

    # Read template containing full UI spec for each input variable from parm file into a DataFrame
    df_inputs = pd.read_excel(
        parm_file,
        sheet_name='input_vals',
        usecols='E:U',
        index_col=0,
        engine='openpyxl',
    )

    prev_input_group_id, prev_checked = None, None

    # Then, read through each record in the df to generate the UI
    for i, id_ in enumerate(df_inputs.index):
        # Get the group that this id belongs to
        input_group_id = df_inputs.loc[id_, 'input_group_id']

        # Set boolean to cover cases where chkbox applies to all widgets for connected widgets
        if (input_group_id == prev_input_group_id) and (prev_checked == False):
            chkd_group = False  # all widgets for the class considered unchecked if first for class is unchecked
        else:
            chkd_group = True

        # Get booleans for checkbox, and secondlife (updated):
        checked = form_chkbox_and_get_chkval(id_, df_inputs, chkd_group, )
        if checked:
            form_hdrs(id_, df_inputs)

        if checked:
            user_input = collect_user_inputval(id_, df_inputs)
        else:  # i.e. if not 'checked', just zeroise the input field
            user_input = 0

        # Add the input value to the dataframe
        df_inputs.loc[id_, 'user_input'] = user_input

        # Before moving on to next record, record cls_or_instc & checked for completed id
        prev_input_group_id = input_group_id
        prev_checked = checked

    # And now, ...the results
    st.header(':page_facing_up: Zoo Rating')
    st.subheader('Because attributes are obviously additive...')
    lov_sum = df_inputs['user_input'][df_inputs['attr'] == 'lovability'].sum()
    scary_sum = df_inputs['user_input'][df_inputs['attr'] == 'scariness'].sum()
    fierce_sum = df_inputs['user_input'][df_inputs['attr'] == 'ferocity'].sum()
    st.write(f"Total lovability is {lov_sum}")
    st.write(f"Total scariness is {scary_sum}")
    st.write(f"Total ferocity is {fierce_sum}")

    st.header(':see_no_evil: Every DS app needs a nonsense chart')
    show_chart = st.checkbox(label='Show a nonsense chart?',
                             value=False,
                             key=str(998),  # String required for streamlit versions after v0.83
                             help=None)
    if show_chart:
        fig = stack_plot(df_inputs)
        st.plotly_chart(fig)


# functions ###########################################################################################################
def form_chkbox_and_get_chkval(id_, df_inputs, chkd_group, ):
    # Get fields required to render chkbox
    chkbox_before = df_inputs.loc[id_, 'chkbox_before']

    if chkbox_before:
        # collect the user input (check (True) or no check (False))
        checked = st.sidebar.checkbox(
            label=df_inputs.loc[id_, 'chkbox_label'],
            value=df_inputs.loc[id_, 'chkbox_value'],
        )
    else:
        checked = True  # input only collected from widget if checked==True /// This is the default

    # Ensure all connected widgets are checked with same boolean value
    # ...(based on chkbox placed before the first of the connected widgets)
    if (checked == True) and (chkd_group == False):  # Remember checked==True is default for all non-checkbox widgets
        checked = False  # ==> override 'True' default and will skip & zeroise this widget in subsequent processing

    return checked


def form_hdrs(id_, df_inputs):
    # Get fields required to render hdr
    header_before = df_inputs.loc[id_, 'header_before']
    header_label = df_inputs.loc[id_, 'header_label']
    if header_before:
        st.sidebar.header(header_label)


def collect_user_inputval(id_, df_inputs, ):
    """
    Forms input widget to collect user input_val and returns value (formatted as rqd for following calcs)
    :param id_: Identifier (index) for this input field
    :param df_inputs: DataFrame holding the template for each ui input
    :return: The input value (formatted as required for use in subsequent calculations) --> input_val
    """
    # Set up some dicts mapping field values in df_inputs to functions
    d_widgets = {'slider': st.sidebar.slider,
                 'number_input': st.sidebar.number_input,
                 'radio': st.sidebar.radio}
    d_num_fmt = {'%d': int, '%.1f': float, '%.2f': float, '%s': str, }

    # Get fields required to render the input widget
    format = df_inputs.loc[id_, 'format_spec']
    # Get type coversion f based on provided 'format_spec'...
    f = d_num_fmt.get(format, float)  # Set to float if fmt_spec not in dict
    min_value = f(df_inputs.loc[id_, 'min_value'])
    max_value = f(df_inputs.loc[id_, 'max_value'])
    value = f(df_inputs.loc[id_, 'default_value'])
    step = f(df_inputs.loc[id_, 'step'])
    desc_label = df_inputs.loc[id_, 'desc_label']  # don't apply f(); not a numeric field
    key = str(df_inputs.loc[id_, 'st_key'])  # Field has to be a string after streamlit v0.83

    widget_spec = df_inputs.loc[id_, 'st_widget']
    widget = d_widgets[widget_spec]

    # Collect input_val & add it to new col in df
    input_val = widget(desc_label,
                       min_value, max_value, value, step,
                       format, key,
                       )

    return input_val


def stack_plot(df):
    fig = px.area(df, x='attr', y='user_input', color='cls_or_instnc')
    fig.update_layout(title="Attributes (stacked)")
    return fig


#######################################################################################################################


if __name__ == "__main__":
    main()
