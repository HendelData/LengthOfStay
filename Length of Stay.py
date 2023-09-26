import pandas as pd
import plotly.express as px
import statsmodels.api as sm

filepath = 'C:/Users/marce/Documents/Python/'

# READ IN DATA
los = pd.read_excel(filepath + 'SWD/Length of Stay/Length of Stay.xlsx', sheet_name='Data2')
los['timeperiod'] = los['timeperiod'].str.slice(5, 7)
los['xCounter'] = range(0, len(los))

# CREATE EMPTY DATAFRAME WITH LOS COLUMNS
los_m = los.drop(los.index)

# CREATE REGRESSION COEFFICIENTS FOR EACH FACET
for i in range(0, 6):
    los1 = los[los['group'] == los['group'][i]]
    los1.loc[:, 'xCounter'] = range(0, len(los1))
    los1.index = range(0, len(los1))

    # COMPUTE REGRESSION COEFFICIENTS
    model1 = sm.OLS(los1['value'], sm.add_constant(los1['xCounter']))
    results1 = model1.fit()

    c = pd.DataFrame(results1.params.iloc[1] * los1['xCounter'] + results1.params.iloc[0], index=range(0, len(los1)))
    c['group'] = los['group'][i]
    c['x_reg'] = range(0, len(los1))
    c['timeperiod'] = los1['timeperiod']
    c.rename(columns={'xCounter': 'y_reg'}, inplace=True)

    m = los.merge(c, on=["timeperiod","group"], how="inner")
    los_m = los_m._append(m)

# CREATE BAR GRAPH
fig = px.bar(los, x="timeperiod", y="value", facet_col="group",
             labels={'group': '', 'timeperiod': ''})

# FORMAT BAR GRAPH
fig.update_layout(bargap=0, bargroupgap=0, plot_bgcolor='rgb(202,222,238)',
                  yaxis=dict(tickformat=".0%", title=''),
                  title_x=0.07,
                  title=dict(font=dict(size=18), text='<b>2019 Post-Surgery Length of Stay</b>'),
                  margin=dict(t=100))

fig.for_each_yaxis(lambda x: x.update(showgrid=True, dtick=0.20))
fig.for_each_xaxis(lambda x: x.update(showgrid=False, zeroline=False))

# FORMAT HOVERDATA AND MARKERS
fig.update_traces(hovertemplate="%{y:0.1%} <extra></extra>",
                  marker_color='rgb(248,240,226)',
                  marker_line=dict(width=0.5, color='gray'))

# REMOVE "=" IN LABEL FOR EACH FACET
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

# CREATE TREND LINES
l = px.line(los_m, x="timeperiod", y="y_reg", facet_col="group",
            labels={'group': '', 'timeperiod': ''}).update_traces(hovertemplate="%{y:0.1%} <extra></extra>",
                                                                  line=dict(color='goldenrod', dash='4px'))

fig.add_traces(l.data)

fig.write_html(filepath + 'Length of Stay.html')
