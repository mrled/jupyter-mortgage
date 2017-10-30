<%page args="apryearly, principal, term, overpayment, appreciation, monthlypayments, yearlypayments" />

<!--
NOTE:   I'm not sure why I need <span> tags around (only some?) calls to dollar(),
        but if I do not include them, Jupyter does something really fucked up to my text.
-->

<%!
# Module-level block (<%! ... %>). Executed only *once*!
from mortgage import MONTHS_IN_YEAR, schedule
from mortgageui import dollar
%>

<h1>Mortgage amortization schedule</h1>

<p>Amortization schedule for a <span>${dollar(principal)}</span> loan over ${term} months at ${apryearly}% interest.</p>

<p>Expect the property to appreciate ${appreciation}% each year.</p>

%if overpayment != 0:
    <%
        # Calculate figures as if no overpayment was applied, for comparative analysis
        no_overpmt_monthly_sched = [month for month in schedule(apryearly, principal, term, overpayments=None, appreciation=0)]
    %>
    <p>With a monthy overpayment of ${dollar(overpayment)}, you can expect to pay off the loan in ${int(len(monthlypayments) / MONTHS_IN_YEAR)} years (${len(monthlypayments)} months), or approximately ${int((len(no_overpmt_monthly_sched) - len(monthlypayments)) / MONTHS_IN_YEAR)} years (${len(no_overpmt_monthly_sched) - len(monthlypayments)} months) faster than the initial ${int(len(no_overpmt_monthly_sched) / MONTHS_IN_YEAR)} year (${len(no_overpmt_monthly_sched)} month) term.
    This means you will pay <span>${dollar(monthlypayments[-1].totalinterest)}</span> in interest over the term of the loan, saving <span>${dollar(no_overpmt_monthly_sched[-1].totalinterest - monthlypayments[-1].totalinterest)}</span> of the full <span>${dollar(no_overpmt_monthly_sched[-1].totalinterest)}</span> that would be paid over the entire term of the loan without an overpayment.</p>
%else:
    <p>With a montly overpayment of ${dollar(0)}, you will pay off the loan in ${int(len(monthlypayments) / MONTHS_IN_YEAR)} years (${len(monthlypayments)} months). This will result in total interest payment of <span>${dollar(monthlypayments[-1].totalinterest)}</span></p>
%endif

<table>

<tr>
    %if yearlypayments:
        <th>Year</th>
    %else:
        <th>Month</th>
    %endif
    <th>Payment</th>
    <th>Remaining principal</th>
    <th>Value</th>
    <th>Equity</th>
    <th>Total interest paid</th>
</tr>

<tr>
    <td>Initial loan amount</td>
    <td></td>
    <td>${dollar(principal)}</td>
    <td>${dollar(principal)}</td>
    <td>${dollar(0)}</td>
    <td>${dollar(0)}</td>
</tr>

<%
    loanpayments = yearlypayments if yearlypayments is not None else monthlypayments
%>
%for payment in loanpayments:
    <tr>
        <td>${payment.index}</td>
        <td>
            <table>
                <tr><th>Total Payment</th><th>${dollar(payment.totalpmt)}</th></tr>
                <tr><td>Minimum Payment</td><td>${dollar(payment.balancepmt + payment.interestpmt)}</td></tr>
                <tr><td>Balance</td><td>${dollar(payment.balancepmt)}</td></tr>
                <tr><td>Interest</td><td>${dollar(payment.interestpmt)}</td></tr>
                <tr><td>Overpayment</td><td>${dollar(payment.overpmt)}</td></tr>
            </table>
        </td>
        <td>${dollar(payment.principal)}</td>
        <td>${dollar(payment.value)}</td>
        <td>${dollar(payment.equity)}</td>
        <td>${dollar(payment.totalinterest)}</td>
    </tr>
%endfor

</table>
