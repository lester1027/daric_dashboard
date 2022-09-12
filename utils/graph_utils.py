def screening_to_str(metrics_screening):
    # convert the metrics screening data to string in the hovertext
    hovertext = f'{"Metric":<20} {"Stock value":^20} {"":<5} {"Benchmark":<10} {"Diff":^10}<br>'
    for metric, details in metrics_screening.items():
        flag, stock_value, symb, benchmark, diff = details

        if flag:
            state = 'Passed'
        else:
            state = 'Failed'
        hovertext = hovertext + f'{metric:<20} {stock_value:^20.3f} {symb + str(benchmark):<10} {diff:^10.3f}<br>'

    return hovertext