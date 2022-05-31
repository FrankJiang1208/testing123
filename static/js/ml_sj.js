d3.json("../static/resources/Salary_Prediction.json").then(function(data) {
    const job=data.Year;
    const job1=data.Year1;
    const loc=data.State;
    const sec=data.Database;

    dropdown1=d3.select("#selDataset1");
    dropdown2=d3.select("#selDataset2");
    dropdown3=d3.select("#selDataset3");

    for (i=0;i<sec.length;i++) {
        let op=dropdown1.append("option").text(sec[i])
        op.property('value',sec[i])
    }

    for (i=0;i<job.length;i++) {
        let op1=dropdown2.append("option").text(job[i])
        op1.property('value',job[i])
    }
    d3.select('#selDataset1').on('change', changeYear);

    function changeYear(){
        let id=dropdown1.property('value');
        if (id=='Annual'){
            dropdown2.selectAll('option').remove()
            for (i=0;i<job.length;i++) {
                let op1=dropdown2.append("option").text(job[i])
                op1.property('value',job[i])
            }
        }else{
            dropdown2.selectAll('option').remove()
            for (i=0;i<job1.length;i++) {
                let op1=dropdown2.append("option").text(job1[i])
                op1.property('value',job1[i])
            }
        }
    }


    for (i=0;i<loc.length;i++) {
        let op3=dropdown3.append("option").text(loc[i])
        op3.property('value',loc[i])
    }


});