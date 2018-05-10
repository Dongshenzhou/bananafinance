from app import mysql
import myiex
import datetime
def pf_summary(username = None, uid = None):
    cur = mysql.connection.cursor()
    if username:
        cur.execute('SELECT * FROM portfolio  NATURAL JOIN users WHERE username=%s', [username])
    elif uid:
        cur.execute('SELECT * FROM portfolio WHERE uid=%s', [uid])
    existed_pf = cur.fetchall()
    pf_dict = {}
    for i in existed_pf:
        i['tickers'] = []
        pf_dict[i['p_name']] = i
    if username:
        cur.execute('SELECT * FROM stocks_of_portfolio NATURAL JOIN users WHERE username=%s', [username])
    elif uid:
        cur.execute('SELECT * FROM stocks_of_portfolio WHERE uid = %s', [uid])
    ticket_in_portfolio = cur.fetchall()
    distinct_symbol = set()
    for i in ticket_in_portfolio:
        pf_dict[i['p_name']]['tickers'].append(i)
        distinct_symbol.add(i['stock_symbol'])
    real_time = myiex.batch_quote_and_oneday(distinct_symbol)
    for pf in pf_dict:
        pf_detail = pf_dict[pf]
        tickers = pf_detail['tickers']
        pf_detail['num_ticker'] = len(tickers)
        total_value = 0
        total_change = 0
        last_close_total_value = 0
        cost_basis = 0
        for symbol in tickers:
            total_value += symbol['volume'] * real_time[symbol['stock_symbol'].upper()]['quote']['latestPrice']
            total_change += symbol['volume'] * real_time[symbol['stock_symbol'].upper()]['quote']['change']
            last_close_total_value += symbol['volume'] * real_time[symbol['stock_symbol'].upper()]['quote'][
                'previousClose']
            if not symbol['price_buy']:
                pf['cost_basis'] = None
            else:
                cost_basis += symbol['price_buy'] * symbol['volume']
        percent_change = 100 * total_change / last_close_total_value if last_close_total_value else None
        pf_detail['total_value'] = total_value if total_value else None
        pf_detail['last_change'] = total_change if total_change else None
        pf_detail['percent_change'] = percent_change if percent_change else None
        pf_detail['previous_close_value'] = last_close_total_value if last_close_total_value else None
        if not 'cost_basis' in pf:
            pf_detail['cost_basis'] = cost_basis if cost_basis else None
        pf_detail['total_change'] = total_value - cost_basis if total_value and cost_basis else None
        pf_detail['total_percent_change'] = (total_value - cost_basis) * 100 / cost_basis if cost_basis else None
    summary_index = ['p_name', 'num_ticker', 'total_value', 'previous_close_value', 'cost_basis', 'last_change', 'percent_change', 'total_change', 'total_percent_change']
    summary = [{k:value[k] for k in summary_index} for value in pf_dict.values()]
    cur.close()
    return summary, summary_index


def add_portfolio(p_name, uid):
    cur = mysql.connection.cursor()
    result = cur.execute('SELECT * FROM portfolio WHERE p_name = s% and uid = s%',[p_name, uid])
    if not result:
        return False
    sql = "INSERT INTO portfolio(p_name, uid, start_date) VALUES (%s, %s, %s)"
    cur.execute(sql,[p_name, uid, str(datetime.date.today())])
    mysql.connection.commit()
    cur.close()
    return True

def delete_portfolio(p_name, uid):
    return

