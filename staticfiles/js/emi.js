

"use strict";

(function ($) {
  $.fn.emiculator = function (options, callback) {


    /*
     * draws table with monthly breakdown of principal and interest
     */
    function drawComponentsTable(data_obj, init_options) {

      var settings = init_options.settings;
      var baseEl = init_options.baseEl;
      var emi_data = data_obj.data_obj;
      var heading = '<h4>' + settings.language.BREAKDOWN_TABLE_HEADING + '</h4>';
      var table = "<div class='breakdown-table-container'><table class='table table-striped'><tr><th>Principal</th><th class='text-center'>Interest</th><th  class='text-right'>Balance</th></tr>"
      var precision = settings.precision;
      $(emi_data).each(function () {
        table += "<tr>";
        table += "<td>" + settings.currency + " " + Math.round(this[0].toFixed(precision)) + "</td>";
        table += "<td class='text-center'>" + settings.currency + " " + Math.round(this[1].toFixed(precision)) + "</td>";

        table += "<td class='text-right'>" + settings.currency + " " + Math.round(this[2].toFixed(precision)) + "</td>";
        table += "</tr>";

      })

      table += "</table></div>";
      $(baseEl + " .emi-table-container").html(heading + table);
    }

    /*
     * update the results inside the html layout 
     */
    function updateDataInHTML(data, init_options) {

      var settings = init_options.settings;
      var baseEl = init_options.baseEl;
      $(baseEl + " .emi-monthly").html(settings.currency + " " + data.emi);
      $(baseEl + " .emi-total-interest").html(settings.currency + " " + data.total_interest);
      $(baseEl + " .emi-total-payment").html(settings.currency + " " + data.total_payment);
      return true;

    }


    /*
     * draws dough nut chart for showing interest and principal components 
     */

    function drawChart(data_obj, init_options) {

      var settings = init_options.settings;
      var baseEl = init_options.baseEl;
      var uniqId = init_options.uniqId;

      $(baseEl + " .emi-chart-container").addClass("col-md-4");
      if (typeof Chart == "undefined") {
        $(baseEl + " .emi-chart").html("<div class='alert text-danger'>For showing charts the widget uses <a href='https://www.chartjs.org' target='_blank'>Chart.js</a>. Please load the Chart.js. See documentation for options</div>");
        return false;
      }

      //remove old chart
      $("canvas#" + uniqId + "-emi-chart").remove();

      $(baseEl + " .emi-chart").html('<canvas id="' + uniqId + '-emi-chart" width="240" height="240"></canvas>');
      var ctx = $("#" + uniqId + "-emi-chart");

      var data = {
        datasets: [{
          data: [data_obj.total_interest, data_obj.principal],
          backgroundColor: settings.backgroundColor,
          hoverBackgroundColor: settings.hoverBackgroundColor,
        }],

        // These labels appear in the legend and in the tooltips when hovering different arcs
        labels: [
          'Total Interest',
          'Prinicpal Loan Amount',
        ],

      };
      var options = new Array();

      var myPieChart = new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: options
      });
    }

    /*
     * draws the complete calculator html markup layout
     */

    function drawCalcForm(init_options) {
      var settings = init_options.settings;
      var baseEl = init_options.baseEl;
      var uniqId = init_options.uniqId;
      var html = '   <h2>' + settings.language.CALCULATOR_HEADING + '</h2>   ' +
        '                         <div class="row d-flex flex-row justify-content-center align-items-center  ' +
        '                         emiculator-widget">  ' +
        '                            <div class="emi-calc-container col-md-4">    ' +
        '                             <p class="text-danger  validation-alert" ></p>    ' +
        '                                     <label  for="emi-principal">' + settings.language.LABEL_PRINICIPAL + '</label>  ' +
        '                                     <div class="input-group mb-3">  ' +
        '     ' +
        '                                       <div class="input-group-prepend">  ' +
        '                                         <span class="input-group-text"  >' + settings.currency + '</span>  ' +
        '                                       </div>   ' +
        '                                       <input type="number" class="form-control js-emic-var emi-principal" data-emic-id="emi-principal" value="' + settings.initPrincipal + '"min="0"  max="' + settings.maxPrincipal + '">   ' +
        '                                     </div>  ' +
        '                                      <label  for="emi-rate">' + settings.language.LABEL_RATE + '</label>  ' +
        '                                     <div class="input-group mb-3">  ' +
        '                                        ' +
        '                                       <div class="input-group-prepend">  ' +
        '                                         <span class="input-group-text"  >%</span>  ' +
        '                                       </div>   ' +
        '                                       <input type="number" class="form-control js-emic-var emi-rate"  data-emic-id="emi-rate" value="' + settings.initRate + '" min="0" max="' + settings.maxRate + '">  ' +
        '                                          ' +
        '                                     </div>  ' +
        '                                     <div class="form-group">   ' +
        '                                       <label  for="emi-time">' + settings.language.LABEL_TIME + '</label>  ' +
        '                                       <input type="number" class="form-control js-emic-var js-time-type emi-time"  data-emic-id="emi-time" value="' + settings.initTime + '" min="0" max="' + settings.maxTime + '">    ' +
        '                                     </div>  ' +
        '                                        ' +
        '                                    <div class="form-group">   ' +
        '                                      <div class="custom-control custom-radio d-inline-block my-1 mr-sm-2">  ' +
        '                                         <input type="radio" class="custom-control-input js-emic-radio-var js-time-type"  name="emi-time-type-' + uniqId + '"  value="months" data-emic-id="emi-time-type-months" checked id="emic-radio-months-' + uniqId + '">   ' +
        '                                         <label class="custom-control-label" for="emic-radio-months-' + uniqId + '">Months</label>  ' +
        '                                       </div>   ' +
        '                                       <div class="custom-control custom-radio d-inline-block my-1 mr-sm-2">  ' +
        '                                         <input type="radio" id="emic-radio-years-' + uniqId + '"  class="custom-control-input  d-inline-block js-emic-radio-var js-time-type"   name="emi-time-type-' + uniqId + '" value="years" data-emic-id="emi-time-type-years">   ' +
        '                                         <label class="custom-control-label" for="emic-radio-years-' + uniqId + '">Years</label>  ' +
        '                                       </div>   ' +
        '                                    </div>     ' +
        '                            </div>   ' +
        '                            <div class="emi-cal-results-container col-md-3">  ' +
        '                               <div class="emi-cal-results text-md-right">  ' +
        '                                  <div class=""><h6>' + settings.language.RESULTS_EMI_HEADING + '</h6>  ' +
        '                                     <h3 class="emi-monthly" data-emic-id="emi-payment">   ' +
        '                                        0  ' +
        '                                     </h3>   ' +
        '                                  </div>  ' +
        '                                  <div class=""><h6>' + settings.language.RESULTS_INTEREST_PAYABLE_HEADING + '</h6>  ' +
        '                                     <h3 class="emi-total-interest" data-emic-id="emi-total-interest">  ' +
        '                                         0  ' +
        '                                     </h3>   ' +
        '                                  </div>  ' +
        '                                  <div class=""><h6>' + settings.language.RESULTS_TOTAL_PAYABLE_HEADING + '</h6>  ' +
        '                                     <h3 class="emi-total-payment" data-emic-id="emi-total-payment">  ' +
        '                                         0  ' +
        '                                     </h3>   ' +
        '                                 </div>   ' +
        '                               </div>   ' +
        '                            </div>  ' +
        '                            <div class="emi-chart  emi-chart-container"  >   ' +
        '                            </div>  ' +
        '                              ' +
        '                            <div  class="emi-table-container col-md-12">  ' +
        '                            </div>     ' +
        '                        </div>  ';


      $(baseEl).html(html);
      $(baseEl + " .validation-alert").hide();

    }
    /* 
     * returns array of [emi : "EMI_AMOUNT" , total_payment : "AMOUNT" , total_interest : "TOTAL_INTEREST" , data_obj : "PI_BREAKDOWN"]
     * where PI_BREAKDOWN denotes prinicpal, interest components 
     */
    function calculateEMI(principal, rate_percent, time_in_months, precision) {

      var EMI;
      var rate_per_month = (rate_percent / 12) / 100; //divide the rate by 100 and 12
      var numr = Math.pow((1 + rate_per_month), time_in_months);
      var denr = (Math.pow((1 + rate_per_month), time_in_months) - 1);

      EMI = principal * rate_per_month * (numr / denr);
      //round the EMI to two decimal points 
      EMI = EMI.toFixed(precision);

      var total_payment = EMI * time_in_months;
      var total_interest = total_payment - principal;

      var data_obj = [];

      var principal_by_month = principal;

      // loop through each month and calculate 
      // each months principal component and the interest component

      for (var i = 1; i <= time_in_months; i++) {
        var each_months_principal, each_months_interest;
        each_months_interest = principal_by_month * rate_per_month;
        var principal_component = EMI - each_months_interest;
        var interest_component = each_months_interest;

        var balance_principal = principal_by_month - principal_component;
        if (balance_principal < 0) {
          balance_principal = 0;
        }
        var single_month_data = [principal_component, interest_component, balance_principal];
        data_obj.push(single_month_data);
        principal_by_month = principal_by_month - principal_component;
      }
      var result = new Array();
      result['principal'] = principal;
      result['time_in_months'] = time_in_months;
      result['rate_percent'] = rate_percent;
      result['emi'] = EMI;
      result['total_interest'] = total_interest.toFixed(precision);
      result['total_payment'] = total_payment.toFixed(precision);
      result['data_obj'] = data_obj;

      return result;
    }
    /*
     * initializes the widget based on provided settings
     */
    function init(init_options) {
      var settings = init_options.settings;
      var baseEl = init_options.baseEl;
      var principal, rate_percent, time;
      var time_in_months;
      var precision = settings.precision;
      var showComponents = settings.showComponents;
      var showChart = settings.showChart;
      var time_type = $(baseEl + " .js-time-type:checked").attr("value");
      principal = $(baseEl + " .emi-principal").val();
      rate_percent = $(baseEl + " .emi-rate").val();
      time = $(baseEl + " .emi-time").val();
      if (principal == "" || rate_percent == "" || time == "") {
        return false;
      }
      if (time_type == "months") {
        time_in_months = time;
        $(baseEl + " .emi-time").attr("max", Math.round(settings.maxTime))
      } else if (time_type == "years") {
        $(baseEl + " .emi-time").attr("max", Math.round(settings.maxTime / 12));
        time_in_months = time * 12;
      }
      var data = calculateEMI(principal, rate_percent, time_in_months, precision);
      updateDataInHTML(data, init_options);
      if (showComponents == true) {
        drawComponentsTable(data, init_options);
      }
      if (showChart == true) {

        drawChart(data, init_options);
      }
    }
    function getLanguageText(settings) {
      var language = {};
      language.LABEL_PRINICIPAL = "Loan Amount";
      language.CALCULATOR_HEADING = "EMI Calculator for Loans";
      language.LABEL_RATE = "Loan Rate";
      language.LABEL_TIME = "Loan Tenure";
      language.RESULTS_EMI_HEADING = "Loan EMI";
      language.RESULTS_INTEREST_PAYABLE_HEADING = "Total Interest Payable";
      language.RESULTS_TOTAL_PAYABLE_HEADING = "Total Payment";
      language.BREAKDOWN_TABLE_HEADING = "Monthly breakdown of EMI in <b>Principal</b> and <b>Interest</b> components";
      language.PRINCIPAL_ERROR = "The loan amount value is larger than the  allowed value. Max value is " + settings.maxPrincipal;;
      language.RATE_ERROR = "The loan rate  value is larger than the allowed value. Max value is " + settings.maxRate;
      language.TIME_ERROR = "The loan tenure   is longer than the allowed value. Max value is " + settings.maxTime + " months or " + (settings.maxTime / 12) + " years";
      return language;
    }
    return $(this).each(function () {
      var settings = $.extend({
        currency: 'NPR',
        precision: 2,
        showChart: true,
        showComponents: true,
        backgroundColor: ["#ed1c24", "#3150a1"],
        hoverBackgroundColor: ["#ca0910", "#173585"],
        initPrincipal: 100000,
        maxPrincipal: 100000000000000,
        initRate: 8.5,
        maxRate: 20,
        initTime: 120,
        maxTime: 360
      }, options);
      var el = $(this);
      var language = getLanguageText(settings);
      settings.language = $.extend(language, options.language);
      var baseEl, uniqId;
      if (el.attr("id") == undefined) {
        var timestamp = new Date().getTime();
        el.attr("id", "emic-calculator-" + timestamp);
        baseEl = "#emic-calculator-" + timestamp;
        uniqId = "emic-calculator-" + timestamp;
      } else {
        baseEl = "#" + el.attr("id");
        uniqId = el.attr("id");
      }
      var init_options = {
        settings: settings,
        baseEl: baseEl,
        uniqId: uniqId
      };
      drawCalcForm(init_options);
      init(init_options);
      var baseEl = init_options.baseEl;
      $("body").on("change", baseEl + " .js-emic-var", function (e) {

        if ($(this).hasClass("emi-principal") == true) {
          if (parseInt($(this).val()) > parseInt(settings.maxPrincipal)) {
            $(this).val(settings.maxPrincipal);
            $(baseEl + " .validation-alert").show().html(settings.language.PRINCIPAL_ERROR);
            return false;
          }
        }
        if ($(this).hasClass("emi-rate") == true) {
          if (parseInt($(this).val()) > parseInt(settings.maxRate)) {
            $(this).val(settings.maxRate);
            $(baseEl + " .validation-alert").show().html(settings.language.RATE_ERROR);
            return false;
          }
        }
        if ($(this).hasClass("emi-time") == true) {
          if (parseFloat($(this).val()) > parseFloat($(this).attr("max"))) {
            $(this).val($(this).attr("max"));
            $(baseEl + " .validation-alert").show().html(settings.language.TIME_ERROR);
            return false;
          }
        }
        $(baseEl + " .validation-alert").hide();

        init(init_options);
      })

      /*
       * bind radio elements for time type : years or months, updating the EMI Calc results,
       * charts and components table
       */
      $("body").on("change", baseEl + " .js-emic-radio-var", function () {
        var time_type = $(baseEl + " .js-time-type:checked").attr("value");
        if (time_type == "months") {
          $(baseEl + " .emi-time").val(settings.maxTime);
          $(baseEl + " .emi-time").attr("max", settings.maxTime);
        } else if (time_type == "years") {
          $(baseEl + " .emi-time").val(Math.round(settings.maxTime / 12));
          $(baseEl + " .emi-time").attr("max", Math.round(settings.maxTime / 12));
        }
        init(init_options);

      })


    })

  }
}(jQuery));
