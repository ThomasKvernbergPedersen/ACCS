from flask import Flask, render_template, request, Response
import gunicorn
import io
import csv
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

app = Flask(__name__)

#visualisering bar chart
def create_bar_chart(data):
    data_list = [{'Domain': key, 'Score': value} for key, value in data.items()]
    
    fig = px.bar(data_list, x='Domain', y='Score', title='Total Score per Domain')
    new_x_labels = ['Suitable Items', 'Feasible Agenda', 'Coherent and dynamic formulation', 'Appropriate Intervention Targets', 'Choosing Suitable Interventions', 'Rationale for Interventions', 'Implementing Interventions', 'Reviewing Interventions', 'Reviewing Homework', 'Choosing Suitable Homework', 'Rationale for Homework', 'Planning Homework', 'Choosing Suitable Measures', 'Implementing Measures', 'Pace', 'Time Management', 'Maintained Focus', 'Interpersonal style', 'Empathic Understanding', 'Collaboration', 'Patient Feedback', 'Reflective Summaries' ]
    # Oppdater utseendet på stolpene
    fig.update_traces(
        marker_color=['#A2D2DF', '#A2D2DF', '#4A628A', '#9B7EBD', '#9B7EBD','#9B7EBD','#9B7EBD','#9B7EBD', '#E6C767', '#E6C767','#E6C767','#E6C767','#898121','#898121', '#F87A53','#F87A53','#F87A53','#0D92F4','#0D92F4','#0D92F4', '#54473F','#54473F'  ],  # Endre fargen på stolpene
        texttemplate='%{x}: %{y}',  # Legg til tekst på stolpene
        textposition='outside'  # Plasser teksten utenfor stolpene
    )
    
    # Oppdater x-aksen med nye navn
    fig.update_xaxes(
        tickvals=list(data.keys()),  # Originale verdier
        ticktext=new_x_labels  # Nye navn
    )
    
    # Oppdater layout for å forbedre utseendet
    fig.update_layout(
        xaxis_title='See your item spesific score in the color separated domains.',
        yaxis_title='Item score',
        title='Total score per Domene',
        uniformtext_minsize=8,
        uniformtext_mode='hide'
    )

    return fig.to_html(full_html=False)



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Samle inn data fra skjemaet
        data = {}
        for key, value in request.form.items():
            if key.startswith('item'):
                data[key] = float(value)  # Konverter til float hvis verdien finnes


         #NAVN og dato
        therapist_name = request.form.get('therapist_name') 
        assessor_name = request.form.get('assessor_name')             
        submission_date = request.form.get('submission_date')

        # Beregn total skåre
        total_score = sum(data.values())

                # Hent tekstfelt
        therapist_strengths = request.form.get('therapist-strengths')
        therapist_needs = request.form.get('therapist-needs')

        # Tekstfelt domene
        strengths1_1 = request.form.get('strengths1_1')
        strengths2_1 = request.form.get('strengths2_1')
        strengths3_1 = request.form.get('strengths3_1')
        strengths4_1 = request.form.get('strengths4_1')
        strengths5_1 = request.form.get('strengths5_1')
        strengths6_1 = request.form.get('strengths6_1')
        strengths7_1 = request.form.get('strengths7_1')
        strengths8_1 = request.form.get('strengths8_1')





        # Mapping dictionary 
        
        complexity_mapping = { "1": "Very Straightforward", "2": "Somewhat Straightforward", "3": "Somewhat Complex", "4": "Very Complex" }
        
        
        # Get the value from the form 
        patient_complexity_value = request.form.get('patient_complexity')
        # Map the value to the descriptive text 
        patient_complexity = complexity_mapping.get(patient_complexity_value, "Unknown Complexity")

            # Tekstfelt domene
        strengths = {
            'Domain 1 - Agenda Setting': strengths1_1,
            'Domain 2 - Formulation': strengths2_1,
            'Domain 3 – CBT Interventions': strengths3_1,
            'Domain 4 – Homework': strengths4_1,
            'Domain 5 – Appropriate Tracking of Progress': strengths5_1,
            'Domain 6 – Effective Use of Time': strengths6_1,
            'Domain 7 – Fostering Therapeutic Relationship': strengths7_1,
            'Domain 8 – Effective Two-way Communication': strengths8_1
        }

        # Bestem kategori

        if  0 <= total_score <= 43:
            category = 'Limited: Therapist fails to include feature outlined. Or therapist demonstrates a significant absence of skill or an inappropriate performance which is likely to have negative therapeutic consequences.'
            category_class = 'Limited'
        elif 44 <= total_score <= 65:
            category = 'Basic: Therapist’s performance is somewhat appropriate with some degree of skill evident. However, major substantive problems are evident.'
            category_class = 'Basic'
        elif 66 <= total_score <= 87:
            category = 'Good: Therapist demonstrates a good degree of skill with no major problems. However, minor problems or inconsistencies are evident in the therapist’s performance.'
            category_class = 'Good'
        elif 88 <= total_score <= 100:
            category = 'Advanced: Therapist consistently demonstrates a high level of skill with only very few and very minor problems.'
            category_class = 'Advanced'
        else:
            category = 'wrong value'
            category_class = 'wrong'



      

            
            


        # Beregn gjennomsnittlig skåre
        average_score = round(total_score / len(data), 2) if data else 0  # Unngå divisjon med null

        # Domenespesifikk informasjon
        domain1_values = {key: value for key, value in data.items() if key.startswith('item1_')}
        domain2_values = {key: value for key, value in data.items() if key.startswith('item2_')}
        domain3_values = {key: value for key, value in data.items() if key.startswith('item3_')}
        domain4_values = {key: value for key, value in data.items() if key.startswith('item4_')}
        domain5_values = {key: value for key, value in data.items() if key.startswith('item5_')}
        domain6_values = {key: value for key, value in data.items() if key.startswith('item6_')}
        domain7_values = {key: value for key, value in data.items() if key.startswith('item7_')}
        domain8_values = {key: value for key, value in data.items() if key.startswith('item8_')}

        # Creating a pandas DataFrame
        df = pd.DataFrame({
            'Domain': ['Suitable Items', 'Feasible Agenda', 'Coherent and dynamic formulation', 
                       'Appropriate Intervention Targets', 'Choosing Suitable Interventions', 
                       'Rationale for Interventions', 'Implementing Interventions', 
                       'Reviewing Interventions', 'Reviewing Homework', 'Choosing Suitable Homework', 
                       'Rationale for Homework', 'Planning Homework', 'Choosing Suitable Measures', 
                       'Implementing Measures', 'Pace', 'Time Management', 'Maintained Focus', 
                       'Interpersonal style', 'Empathic Understanding', 'Collaboration', 'Patient Feedback', 
                       'Reflective Summaries', 'Total Score'],
            'Response': [
                data.get('item1_1', ''), data.get('item1_2', ''), 
                data.get('item2_1', ''), data.get('item3_1', ''), data.get('item3_2', ''), 
                data.get('item3_3', ''), data.get('item3_4', ''), data.get('item3_5', ''), 
                data.get('item4_1', ''), data.get('item4_2', ''), data.get('item4_3', ''), data.get('item4_4', ''), 
                data.get('item5_1', ''), data.get('item5_2', ''),
                data.get('item6_1', ''), data.get('item6_2', ''), data.get('item6_3', ''), 
                data.get('item7_1', ''), data.get('item7_2', ''), data.get('item7_3', ''), 
                data.get('item8_1', ''), data.get('item8_2', ''), total_score
            ],
            'Feedback': [
                strengths1_1, '',  
                strengths2_1, 
                strengths3_1, '', '', '', '', 
                strengths4_1, '', '', '', 
                strengths5_1, '', 
                strengths6_1, '', '',  
                strengths7_1, '', '',  
                strengths8_1, '', 
                therapist_needs
            ]
        })

        # Convert DataFrame to HTML table
        df_html = df.to_html(classes='table table-striped')

        # Save DataFrame for downloading 
        df.to_csv('responses.csv', index=False) 
        df.to_excel('responses.xlsx', index=False)



        
                    # Funksjon for å beregne gjennomsnittet av verdier i en dictionary
        def calculate_average(domain_values):
            if len(domain_values) == 0:
                return 0
            return sum(domain_values.values()) / len(domain_values)

        # Beregn gjennomsnitt for hvert domene
        average_domain1 = calculate_average(domain1_values)
        average_domain2 = calculate_average(domain2_values)
        average_domain3 = calculate_average(domain3_values)
        average_domain4 = calculate_average(domain4_values)
        average_domain5 = calculate_average(domain5_values)
        average_domain6 = calculate_average(domain6_values)
        average_domain7 = calculate_average(domain7_values)
        average_domain8 = calculate_average(domain8_values)

                # Domenesnitt
        domain_averages = {
            'Domain 1 - Agenda Setting': average_domain1,
            'Domain 2 - Formulation': average_domain2,
            'Domain 3 – CBT Interventions': average_domain3,
            'Domain 4 – Homework': average_domain4,
            'Domain 5 – Appropriate Tracking of Progress': average_domain5,
            'Domain 6 – Effective Use of Time': average_domain6,
            'Domain 7 – Fostering Therapeutic Relationship': average_domain7,
            'Domain 8 – Effective Two-way Communication': average_domain8
        }

        # Finn domenet med høyest og lavest gjennomsnitt
        max_domain = max(domain_averages, key=domain_averages.get)
        min_domain = min(domain_averages, key=domain_averages.get)

                        # Hent tilbakemeldingene for max_domain og min_domain
        max_domain_feedback = strengths[max_domain]
        min_domain_feedback = strengths[min_domain]



        



        # Lag visualiseringer

        bar_chart = create_bar_chart(data)
        bar_chart1 = create_bar_chart(domain1_values)


            




       

        return render_template('result.html', total_score=total_score, category=category, average_score=average_score, therapist_strengths = therapist_strengths, therapist_needs = therapist_needs,
                               strengths1_1 = strengths1_1, strengths2_1 = strengths2_1, strengths3_1 = strengths3_1, strengths4_1 = strengths4_1, strengths5_1 = strengths5_1, strengths6_1 = strengths6_1, strengths7_1 = strengths7_1,
                               strengths8_1 = strengths8_1, max_domain_feedback = max_domain_feedback, min_domain_feedback = min_domain_feedback,
                               domain1_values=domain1_values, domain2_values=domain2_values, domain3_values=domain3_values,
                               domain4_values=domain4_values, domain5_values=domain5_values, domain6_values=domain6_values,
                               domain7_values=domain7_values, domain8_values=domain8_values, patient_complexity=patient_complexity, 
                               bar_chart=bar_chart,
                               category_class=category_class, bar_chart1 = bar_chart1, max_domain = max_domain, min_domain = min_domain, therapist_name=therapist_name, assessor_name=assessor_name, submission_date=submission_date, df_html=df_html)

    return render_template('index.html')

@app.route('/download_csv') 
def download_csv(): 
    df = pd.read_csv('responses.csv') 
    csv = df.to_csv(index=False) 
    response = Response(csv, mimetype="text/csv") 
    response.headers["Content-Disposition"] = "attachment; filename=responses.csv" 
    return response 

@app.route('/download_excel') 
def download_excel(): 
    df = pd.read_excel('responses.xlsx') 
    output = io.BytesIO() 
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer: 
        df.to_excel(writer, index=False, sheet_name='Sheet1') 
        writer._save() 
    output.seek(0) 
    response = Response(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") 
    response.headers["Content-Disposition"] = "attachment; filename=responses.xlsx" 
    return response

if __name__ == '__main__':
    app.run(debug=True)



