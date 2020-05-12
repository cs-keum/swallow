//$(document).ready(function() {

function show_table(tabledata) {
//$(function () {
        var table = new Tabulator(document.getElementById('example-table'), {
            height:"100%", // set height of table (in CSS or here), this enables the Virtual DOM and improves render speed dramatically (can be any valid css height value)
            layout:"fitColumns", //fit columns to width of table (optional)
            columns:[ //Define Table Columns
                {title:"코드", field:"stock_code", width:100},
                {title:"종목명", field:"stock_name", width:100, align:"left"},
                {title:"산업분야", field:"stock_sector", width:180},
                {title:"산업코드", field:"industry_code", width:50},
<!--                {title:"capital_value", field:"capital_value", width:100, formatter:"money", formatterParams:{precision:false}},-->
<!--                {title:"listed_stocks", field:"listed_stocks", width:100, formatter:"money", formatterParams:{precision:false}},-->
                {title:"거래량", field:"trading_volume", width:80, formatter:"money", formatterParams:{precision:false}},
                {title:"시가총액", field:"total_market_price", width:140, formatter:"money", formatterParams:{precision:false}},
                {title:"영업현금흐름", field:"cash_flows", width:140, formatter:"money", formatterParams:{precision:false}},
                {title:"인수금회수(년)", field:"total_market_price_cash_flows_ratio", width:50, formatterParams:{precision:false}},
                {title:"외국인보유율", field:"foreign_holding_ratio", width:70, formatterParams:{precision:false}},
                {title:"초과수익", field:"excess_profit", width:100, formatter:"money", formatterParams:{precision:0}},
                {title:"매수가율", field:"price_gap_ratio", width:40, formatterParams:{precision:false}},
                {title:"현재가", field:"price", width:80, formatter:"money", formatterParams:{precision:false}},
                {title:"매수가", field:"buy_price", width:80, formatter:"money", formatterParams:{precision:false}},
                {title:"1차매도", field:"adequate_price", width:80, formatter:"money", formatterParams:{precision:false}},
                {title:"2차매도", field:"excess_price", width:80, formatter:"money", formatterParams:{precision:false}},
                {title:"PER", field:"per", width:50},
                {title:"BPR", field:"bpr", width:50},
                {title:"배당금", field:"dividend", width:50},
                {title:"배당률", field:"dividend_yield", width:50},
                {title:"ROE", field:"roe", width:80},
                {title:"ROEs", field:"roes",formatter:function(cell, formatterParams, onRendered){
                        return JSON.stringify(cell.getValue())
                    }
                },
            ],
            rowClick:function(e, row){ //trigger an alert message when the row is clicked
                alert(JSON.stringify(row.getData()));
            },
        });

//        var tabledata = JSON.parse(document.getElementById("data").dataset.stock);
//        var tabledata = JSON.parse($("#data").data("stock"));
//        var tabledata = {{stocks_recommended|tojson}} ;
        table.setData(tabledata);
};