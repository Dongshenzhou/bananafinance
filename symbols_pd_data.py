import myiex
import pandas
def batch_csv(symbols):
    result = myiex.multi_1year_data(symbols)
    print(result)
    mydict = {i:{ j["date"]:j["close"] for j in result[i.upper()]["chart"]} for i in symbols}
    df = pandas.DataFrame.from_dict(mydict, orient='columns')
    return df

    filename = "Year_Data"
    # w = csv.DictWriter(sys.stdout, head)
    # for key, val in sorted(mydict.items()):
    #     row = {'date': key}
    #     row.update(val)
    #     w.writerow(row)

    # for i in symbols:
    #     filename += "_{}".format(i)
    # filename += ".csv"
    # with open(filename,'wb') as csvfile:
    #     w = csv.DictWriter(csvfile, head)
    #     for k in mydict:
    #         w.writerow({field: mydict[k].get(field) or k for field in head})

# symbols = ['fb','msft', 'googl','aapl']
# pddict = batch_csv(symbols)
# df = pandas.DataFrame.from_dict(pddict, orient='columns')
# print (df)
