import json
from github import Github
import streamlit as st
import base64
import pandas as pd
from datetime import datetime
from PIL import Image
import pytz
import io
from io import BytesIO
import git_backend as gb
import os
st.set_page_config(
    layout="wide",
    page_title='facility_w',
    page_icon='🪙')

egypt_tz = pytz.timezone('Africa/Cairo')
# GitHub setup
g = Github(st.secrets["GITHUB_TOKEN"])
repo = g.get_repo(st.secrets["REPO_NAME"])

def load_data(file_path):
    if file_path not in ("check list.json", "change log.json",'work order records.json','completed work order.json'):
        return None
    try:
        content = repo.get_contents(file_path)
        data = json.loads(content.decoded_content.decode())
    except:
        # If file does not exist or is not accessible, return a default structure based on the file type
        if file_path == "check list.json":
            data = {"check": []}
        elif file_path == "change log.json":
            data = {"logs": []}
        elif file_path == "work order records.json":
            data = {"records": []}  # Adjust according to the structure of work order records
        elif file_path == "completed work order.json":
            data = {"completed": []}  # Adjust according to the structure of completed work orders
    return data

def save_data(file_path, data):
    try:
        content = repo.get_contents(file_path)
        repo.update_file(file_path, f"Update {file_path}", json.dumps(data, indent=2), content.sha)
    except:
        repo.create_file(file_path, f"Create {file_path}", json.dumps(data, indent=2))


# Handle Images
def save_image(image_data, image_name):
    try:
        image_path = f"images/{image_name}"
        encoded_image = base64.b64encode(image_data)

        try:
            content = repo.get_contents(image_path)
            repo.update_file(image_path, f"Update {image_name}", encoded_image, content.sha)
        except:
            repo.create_file(image_path, f"Create {image_name}", encoded_image)
        return image_path
    except Exception as e:
        st.error(f"Error saving image: {str(e)}")
        return None

# Checklist CRUD operations
def create_checklist_record(record):
    data = load_data("check list.json")
    new_record = {
        "id": record.get("id", str(len(data["check"]) + 1)),
        "Location": record.get("Location", ""),
        "Element": record.get("Element", ""),
        "Detector Name": record.get("Detector Name", ""),
        "Date": record.get("Date",""),
        "Rating": record.get("Rating", ""),
        "Comment": record.get("Comment", ""),
    }
    data["check"].append(new_record)
    save_data("check list.json", data)
    return new_record

def update_checklist_record(record_id, updated_data):
    data = load_data("check list.json")
    for record in data["check"]:
        if record["id"] == record_id:
            record.update(updated_data)
            save_data("check list.json", data)
            return record
    return None

def create_work_order(work):
    data = load_data("work order records.json")
    new_record = {
        "id": work.get("id", str(len(data["records"]) + 1)),
        "Location": work.get("Location", ""),
        "Element": work.get("Element", ""),
        "Detector Name": work.get("Detector Name", ""),
        "Date": work.get("Date",""),
        "Rating": work.get("Rating", ""),
        "Responsible Person": work.get("Responsible Person", ""),
        "Expected Repair Date": work.get("Expected Repair Date", ""),
        "Actual Repair Date": work.get("Actual Repair Date", ""),
        "Image": work.get("Image", ""),
        "Comment": work.get("Comment", ""),
        "Safety related": work.get("Safety related", ""),
        "Quality related": work.get("Quality related", "")
    }
    data["records"].append(new_record)
    save_data("work order records.json", data)
    return new_record 
   

def update_work_order(work_id, updated_data):
    data = load_data("work order records.json")
    for record in data["records"]:
        if record["id"] == work_id:
            record.update(updated_data)
            save_data("work order records.json", data)
            return record
    return None

def create_completed_work_order(completed):
    data = load_data("completed work order.json")
    new_record = {
        "id": completed.get("id", str(len(data["completed"]) + 1)),
        "location": completed.get("location", ""),
        "element": completed.get("element", ""),
        "Detector Name": completed.get("Detector Name", ""),
        "Date": completed.get("Date",""),
        "Rating": completed.get("Rating", ""),
        "Responsible Person": completed.get("Responsible Person", ""),
        "Expected Repair Date": completed.get("Expected Repair Date", ""),
        "Actual Repair Date": completed.get("Actual Repair Date", ""),
        "image": completed.get("image", ""),
        "comment": completed.get("comment", ""),
        "Safety related": completed.get("Safety related", ""),
        "Quality related": completed.get("Quality related", "")
    }
    data["completed"].append(new_record)
    save_data("completed work order.json", data)
    return new_record

def update_completed_work_order(completed_id, updated_data):
    data = load_data("completed work order.json")
    for record in data["completed"]:
        if record["id"] == completed_id:
            record.update(updated_data)
            save_data("completed work order.json", data)
            return record
    return None

def create_change_log_entry(entry):
    data = load_data("change log.json")
    new_entry = {
        "id": str(len(data["logs"]) + 1),
        "Modifier Name": entry.get("Modifier Name", ""),
        "Modification Date": entry.get("Modification Date"),
        "Modification Type": entry.get("Modification Type", ""),
        "New Date": entry.get("New Date", "")
    }
    data["logs"].append(new_entry)
    save_data("change log.json", data)
    return new_entry



def load_work_order():
    data = gb.load_data("work order records.json")
    if data:
        df = pd.DataFrame(data["records"])
        for col in ['Date', 'Expected Repair Date', 'Actual Repair Date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        return df
    return pd.DataFrame(columns=[
        'id', 'Location', 'Element', 'Detector Name', 
        'Date', 'Rating', 'Responsible Person', 
        'Expected Repair Date', 'Actual Repair Date', 'Image', 'Comment', 'Safety related','Quality related'
    ])

def load_check_list():
    data = gb.load_data("check list.json")
    if data:
        return pd.DataFrame(data["check"])
    return pd.DataFrame(columns=[
        'id', 'Location', 'Element', 
        'Detector Name', 'Date','Rating','Comment'
    ])



def load_completed_work_order():
    data = gb.load_data("completed work order.json")
    if data:
        return pd.DataFrame(data["completed"])
    return pd.DataFrame(columns=[
        'id', 'modifierName', 'modificationDate', 
        'modificationType', 'newDate'
    ])


def load_change_log():
    data = gb.load_data("change_log.json")
    if data:
        return pd.DataFrame(data["logs"])
    return pd.DataFrame(columns=[
        'id', 'Location', 'Element', 'Detector Name', 
        'Date', 'Rating', 'Responsible Person', 
        'Expected Repair Date', 'Actual Repair Date', 'Image', 'Comment', 'Safety related','Quality related'
    ])

# Initialize session state
if 'check_list_df' not in st.session_state:
    st.session_state.check_list_df = load_check_list()

if 'work_order_df' not in st.session_state:
    st.session_state.work_order_df = load_work_order()

if 'ompleted_work_df' not in st.session_state:
    st.session_state.ompleted_work_df = load_completed_work_order()

if 'log_df' not in st.session_state:
    st.session_state.log_df = load_change_log()



checklist_items = {
    "Floors": [
        "Inspect floors for visible damage and stains"
    ],
    "Lights": [
        "Ensure all light fixtures are operational."
    ],
    "Electrical Outlets": [
        "Inspect all electrical outlets for visible damage",
        "Ensure all outlet covers are installed properly and not damaged.",
        "Verify all electrical outlets are labeled"
    ],
    "Doors": [
        "Inspect door for visible damage and paint chipping",
        "Check door hardware for proper operation (badge access, door handles)",
        "Ensure doors close and latch properly",
        "Inspect door seals"
    ],
    "Ceilings": [
        "Inspect ceilings for visible damage (including cracks, dings, dents, holes) and paint chipping",
        "Inspect ceiling penetrations around piping and ducting to ensure seals fully cover any gaps",
        "Sealing material is not dry or cracked"
    ],
    "Walls": [
        "Inspect walls for visible damage (including cracks, dings, dents, holes) and paint chipping",
        "Inspect all wall penetrations around piping to ensure seals fully cover any gaps and holes",
        "Sealing material is not dry or cracked."
    ],
    "Windows": [
        "Inspect windows for visible damage and cracks",
        "Inspect exterior window seals for cracking, holes, and gaps",
        "Inspect curtains for visible damage and standardize"
    ],
    "Visuals": [
        "Inspect visuals for visible damage or fading",
        "Ensure visuals are updated"
    ],
    "Fixtures and fittings": [
        "Inspect fixtures such as faucets, WC bowls, bathroom sinks, mirrors, etc.",
        "Inspect cafeteria & coffee corner fittings (coffee machines, kettles, Bain Marie, etc.)",
        "Inspect fixture and fitting condition for visible damage"
    ],
    "Furniture": [
        "Inspect movable office furniture, desks, chairs, sofas, tables, cabinets, etc.",
        "Inspect furniture condition for visible damage"
    ]
}

repair_personnel = ['shehab', 'sameh', 'kaleed', 'yasser', 'masry',"zeinab",'wael']


def get_next_event_id():
    if st.session_state.work_order_df.empty or 'event id' not in st.session_state.work_order_df.columns:
        return 'Work Order 1'

    event_ids = st.session_state.work_order_df['event id'].dropna().tolist()

    if not event_ids:
        return 'Work Order 1'

    try:
        last_id = event_ids[-1]
        if isinstance(last_id, str):
            last_num = int(last_id.split(' ')[-1])
        else:
            last_num = 0
    except (ValueError, IndexError):
        last_num = 0

    next_num = last_num + 1
    return f'Work Order {next_num}'

page = st.sidebar.radio('Select page', ['Event Logging', 'Work Shop Order', 'View Change Log','Clear data'])

if page == 'Event Logging':
    work_order = load_check_list()
    col1, col2 = st.columns([2, 0.5])
    with col1:
        st.markdown("""
                <h2 style='text-align: center; font-size: 40px; color: #A52A2A;'>
                    Facility Maintenance Checklist:
                </h2>
                """, unsafe_allow_html=True)
    with col2:
        st.button("Update page",key='Update 2')
        search_keyword = st.session_state.get('search_keyword', '')
        search_keyword = st.text_input("Enter keyword to search:", search_keyword)
        search_button = st.button("Search")
        search_option = 'All Columns'    
    def search_in_dataframe(df_Material, keyword, option):
        if option == 'All Columns':
            result = df_Material[df_Material.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)]
        else:
            result = df_Material[df_Material[option].astype(str).str.contains(keyword, case=False)]
        return result
    if st.session_state.get('refreshed', False):
        st.session_state.search_keyword = ''
        st.session_state.refreshed = False
    if search_button and search_keyword:
        st.session_state.search_keyword = search_keyword
        search_results = search_in_dataframe(st.session_state.work_order_df, search_keyword, search_option)
        st.write(f"Search results for '{search_keyword}'in{search_option}:")
        st.dataframe(search_results, width=1000, height=200)
    st.session_state.refreshed = True

    
    col1, col2 = st.columns([2, 6])
    with col1:
        st.markdown(f"<h3 style='color:black; font-size:30px;'>Select Location:</h3>", unsafe_allow_html=True)
        locations = ['Admin indoor', 'QC lab & Sampling room', 'Processing', 'Receiving area & Reject room',
                     'Technical corridor', 'Packaging', 'Warehouse', 'Utilities & Area Surround',
                     'Outdoor & security gates', 'Electric rooms', 'Waste WTP & Incinerator',
                     'Service Building & Garden Store', 'Pumps & Gas Rooms']
    
        selected_location = st.selectbox('Choose form these areas',locations)
        if selected_location:
            st.markdown(
            f'<p style="font-size: 23px; color: green;">You selected: <span style="font-size: 25px; color: #A52A2A;">{selected_location}</span></p>'
            '<hr style="border: 1px solid  black;"/>', 
            unsafe_allow_html=True
        )

    
    col1, col2 = st.columns([3,3])
    with col1:
        for category, items in checklist_items.items():
            st.markdown(f"<h3 style='color:green; font-size:30px;'>{category}.</h3>", unsafe_allow_html=True)
            for item in items:
                st.markdown(f"<span style='color:blue; font-size:18px;'>* {item}</span>", unsafe_allow_html=True)
                
            col1a, col2a, col3a, col4a = st.columns([1, 2, 2, 2])
            Event_Detector_Name = col2a.text_input('Detector Name', key=f"detector_name_{category}_{selected_location}")
            Rating = col1a.selectbox('Rating', [0, 1, 2, 3, 'N/A'], key=f"rating_{category}_{selected_location}")
            comment = col3a.text_input('Comment', key=f"comment_{category}_{selected_location}")
            responsible_person = col4a.selectbox('Responsible Person', [''] + repair_personnel, key=f"person_{category}_{selected_location}")
            uploaded_file = st.file_uploader(f"Upload Image ({category})", type=["jpg", "jpeg", "png"], key=f"image_{category}_{selected_location}")
            
            if Rating in [1, 2, 3]: 
                st.markdown(f"<p style='color: red; font-size: 22px;'><b>Is this Safety related?</b></p>", unsafe_allow_html=True)
                risk_value = st.checkbox('Safety related?', key=f'high_risk_checkbox_{category}_{selected_location}')
                st.markdown(f"<p style='color: red; font-size: 22px;'><b>Is this Quality related?</b></p>", unsafe_allow_html=True)
                Quality_value = st.checkbox('Quality related?', key=f'Quality_related_checkbox_{category}_{selected_location}')
            else:
                risk_value = None
                Quality_value = None
            button_key = f"add_{category}_{selected_location}"
            
            if st.button(f'Add', key=button_key):
                if Rating in [0, 'N/A']:
                    event_id = 'check'
                    new_check_row = {
                        'id': event_id,
                        'location': selected_location,
                        'Rating': Rating,
                        'Element': category,
                        'Event Detector Name': Event_Detector_Name,
                        'Date': datetime.now(egypt_tz).strftime("%Y-%m-%d %H:%M:%S"),
                        'comment': comment}
                    
                    gb.create_checklist_record(new_check_row)
                    st.session_state.check_list_df = load_check_list()
                    st.success(f"Event recorded successfully! '{category}'!")
                else:
                    event_id = 'work_order' + str(length + 1)
                image_path = ""
                if uploaded_file is not None:
                    try:
                        image = Image.open(uploaded_file)
                        if image.mode == "RGBA":
                            image = image.convert("RGB")
                        max_size = (800, 600)
                        image.thumbnail(max_size)
                        image_buffer = BytesIO()
                        image.save(image_buffer, format="JPEG")
                        image_data = image_buffer.getvalue()
                        ext=uploaded_file.name.split('.')[-1]
                        image_name = f"{event_id}.txt"
                        image_path = gb.save_image(image_data, image_name)
                        if image_path:
                            st.success(f"Image saved successfully as {image_name}")
                        else:
                            st.error("Failed to save the image")
                    except Exception as e:
                        st.error(f"An error occurred while saving the image: {str(e)}")
                        image_path = ""
                            
                    new_order = {
                        'id': event_id,
                        'Location': selected_location,
                        'Element': category,
                        'Event Detector Name': Event_Detector_Name,
                        'Date': datetime.now(egypt_tz).strftime("%Y-%m-%d %H:%M:%S"),
                        'Rating': Rating,
                        'Comment': comment,
                        'Responsible Person': responsible_person,
                        'Expected Repair Date': '',
                        'Actual Repair Date': '',
                        'Image': image_path,
                        'Safety related': 'Yes' if risk_value else 'No',
                        'Quality related': 'Yes' if Quality_value else 'No'
                    }
                    
                    gb.create_work_order(new_order)
                    st.session_state.work_order_df = load_work_order()
                    st.success(f"Event recorded successfully! '{category}'!") 
    
    with col2:
        st.markdown("""
        <div style="border: 2px solid #ffeb3b; padding: 20px; background-color: #e0f7fa; color: #007BFF; border-radius: 5px; width: 100%">
            <h4 style='text-align: center;color: blue;'>Inspection Rating System.</h4>
            <ul style="color: green;">
                <li style="font-size: 18px;">0: Good condition. Well, maintained, no action required. Satisfactory Performance</li>
                <li style="font-size: 18px;">1: Moderate condition. Should monitor. Satisfactory Performance.</li>
                <li style="font-size: 18px;">2: Degraded condition. Routine maintenance and repair needed. Unsatisfactory Performance.</li>
                <li style="font-size: 18px;">3: Serious condition. Immediate need for repair or replacement. Unsatisfactory Performance.</li>
                <li style="font-size: 18px;">N/A :Not applicable</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
                <h2 style='text-align: center; font-size: 30px; color: #A52A2A;'>
                    checklist record:
                </h2>
                """, unsafe_allow_html=True)
        
        latest_data = gb.load_data("check list.json")
        if latest_data and "check" in latest_data:
            df = pd.DataFrame(latest_data["check"])
            st.dataframe(df)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            # Download button
            st.download_button(
                    label="Download Checklist as CSV",
                    data=csv_data,
                    file_name='checklist_records.csv',
                    mime='text/csv',
                   key='download_checklist')
        st.markdown("""
            <h2 style='text-align: center; font-size: 30px; color: #A52A2A;'>
                Facility Maintenance:
            </h2>
            """, unsafe_allow_html=True)
        
        work_data = gb.load_data("work order records.json")
        if work_data and "records" in work_data:
            df = pd.DataFrame(work_data["records"])
            st.dataframe(df)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            # Download button
            st.download_button(
                    label="Download Checklist as CSV",
                    data=csv_data,
                    file_name='checklist_records.csv',
                    mime='text/csv',
                   key='download_work_data')

        else:
            st.write("No checklist data available.")


if page == 'Work Shop Order':
    st.markdown("""
                <h2 style='text-align: center; font-size: 35px; color: #A52A2A;'>
                    Work Shop Order status:
                </h2>
                """, unsafe_allow_html=True)

    # إنشاء تخطيط أفقي بعمودين
    col1, col2 = st.columns([2, 3])

    # الجزء الأول: لاختيار رقم الحدث وإدخال اسم المعدل
    with col1:
        if not st.session_state.work_order_df.empty:
            selected_names = st.multiselect('Select Responsible Person(s)', repair_personnel)
            
            filtered_events = st.session_state.work_order_df[st.session_state.work_order_df['Responsible Person'].isin(selected_names)]

            if not filtered_events.empty:
                event_ids = filtered_events['id'].tolist()
                selected_event_id = st.selectbox('Select Event ID', event_ids)

                if selected_event_id:
                    selected_event = filtered_events[filtered_events['id'] == selected_event_id]
                    if not selected_event.empty:
                        st.session_state.selected_event = selected_event  # حفظ الحدث المحدد في الحالة

                modifier_name = st.text_input('Modifier Name')

                if modifier_name in repair_personnel:
                    Expected_repair_Date = st.date_input('Expected repair Date')
                    Actual_Repair_Date = st.date_input('Actual Repair Date')
                    update_start_button = st.button('Update Expected repair Date')
                    update_end_button = st.button('Update Actual Repair Date')

                    
                    if update_start_button:
                        if selected_event_id in st.session_state.work_order_df['id'].values:
                            updated_data = {
                                'Expected Repair Date': Expected_repair_Date.strftime("%Y-%m-%d %H:%M:%S")
                            }
                            gb.update_work_order(selected_event_id, updated_data)
                            st.success('Expected repair Date Updated successfully')
                            
                            new_log_entry = {
                                'event id': selected_event_id,
                                'modifierName': modifier_name,
                                'modificationDate': datetime.now(egypt_tz).strftime("%Y-%m-%d %H:%M:%S"),
                                'modificationType': 'update Expected repair Date',
                                'newDate': Expected_repair_Date.strftime("%Y-%m-%d %H:%M:%S")
                            }
                            gb.create_change_log_entry(new_log_entry)

                    if update_end_button:
                        if selected_event_id in st.session_state.work_order_df['id'].values:
                            updated_data = {
                                'Actual Repair Date': Actual_Repair_Date.strftime("%Y-%m-%d %H:%M:%S")
                            }
                            gb.update_work_order(selected_event_id, updated_data)
                            st.success('Actual Repair Date Updated successfully')
                            
                            new_log_entry = {
                                'event id': selected_event_id,
                                'modifierName': modifier_name,
                                'modificationDate': datetime.now(egypt_tz).strftime("%Y-%m-%d %H:%M:%S"),
                                'modificationType': 'update Actual Repair Date',
                                'newDate': Actual_Repair_Date.strftime("%Y-%m-%d %H:%M:%S")
                            }
                            gb.create_change_log_entry(new_log_entry)
                            
            else:
                st.warning("No events found for the selected person(s).")
        else:
            st.warning("No checklist data available.")

    with col2:
            if 'selected_event' in st.session_state and not st.session_state.selected_event.empty:
                selected_event = st.session_state.selected_event
                
                # عرض تفاصيل الحدث ك DataFrame
                st.dataframe(selected_event)
    
                # Display the image if it exists
                image_path = selected_event['image'].iloc[0]
                if image_path:
                    try:
                        # Get the encoded image content from GitHub 
                        image_content = gb.repo.get_contents(image_path)
                        decoded_image_data = base64.b64decode(image_content.decoded_content)
                        
                        # Open the image using PIL
                        image = Image.open(BytesIO(decoded_image_data))
                             
                        # Display the image
                        st.image(image, caption=f'Image for Event {selected_event["id"].values[0]}', use_column_width=True)
                    
                    except Exception as e:
                        st.warning(f"Error loading image: {str(e)}")
                else:
                    st.warning("No image available for this event.")
            else:
                st.warning("Select an event to view details.")

            st.markdown("""
            <h2 style='text-align: center; font-size: 27px; color: #A52A2A;'>
                completed work order:
            </h2>
            """, unsafe_allow_html=True)
        
            completed_data = gb.load_data("completed work order.json")
            if completed_data and "completed" in completed_data:
                df = pd.DataFrame(completed_data["completed"])
                st.dataframe(df)
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                # Download button
                st.download_button(
                        label="Download completed_data as CSV",
                        data=csv_data,
                        file_name='completed_data.csv',
                        mime='text/csv'
                    )


elif page == 'View Change Log':
    st.title('View Change Log')
    change_log = load_change_log()
    st.write(change_log)

    df = pd.DataFrame(change_log)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    # Download button
    st.download_button(
            label="Download Checklist as CSV",
            data=csv_data,
            file_name='checklist_records.csv',
            mime='text/csv'
        )


# Page 4: Clear Data
elif page == 'Clear data':
    st.title('Clear Data')

    if st.button('Clear Checklist Data'):
        gb.save_data("checklist.json", {"records": []})
        st.session_state.checklist_df = load_checklist_data()
        st.success('Checklist data cleared!')
        # Delete all files in the images folder
        try:
            contents = gb.repo.get_dir_contents("images")
            for content_file in contents:
                gb.repo.delete_file(
                    content_file.path,
                    "Deleting image file",
                    content_file.sha
                )
            st.success('Checklist data and all images cleared!')
        except Exception as e:
            st.warning(f"Error clearing images: {str(e)}")
            st.success('Checklist data cleared, but there was an issue clearing images.')

    if st.button('Clear Log Data'):
        gb.save_data("change_log.json", {"logs": []})
        st.session_state.log_df = load_change_log()
        st.success('Log data cleared!')
