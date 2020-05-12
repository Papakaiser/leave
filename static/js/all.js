var oneDay = 60*60*1000*24;


 var startDateSelected = function (instance, startDate) {
        console.log("Start date cliekd", startDate);
        $('#nofdays').trigger('input');
 } ;


 var endDateSelected = function (instance, endDate) {
        console.log("End date cliekd", endDate);
        var startDate = $('#startdate').val();
        if(!startDate) {
            return;
        }
        startDate = new Date(startDate);
        var validDays = 1;
        var nextDay = startDate;
        console.log("Checking for day", nextDay);
        while(nextDay.getTime() < endDate.getTime()) {
            nextDay = new Date(nextDay.getTime() + oneDay);
            //check if it's not a weekend and not a holiday
            if(nextDay.getDay() !== 0
            && nextDay.getDay() !== 6
            && !disabledDates.find(h => h.getTime() === nextDay.getTime())) {
            console.log("Valid day found", validDays+1, nextDay)
                ++validDays;
            }
        }
        console.log("Checks done")
        $('#nofdays').val(validDays);


    } ;




 $(document).ready( function () {
     $('#nofdays').on('input', function () {
        console.log("no of days clicked ", $(this).val());
        var startDate = $('#startdate').val();
        if(!startDate) {
            return;
        }
        startDate = new Date(startDate);
        var daysWanted = $(this).val();
        var validDays = 1;
//        const oneDay = 60*60*1000*24;
        var nextDay = startDate;
        while(validDays < parseInt(daysWanted) && nextDay.getYear() === new Date().getYear()) {
            //add one day and check if it is valid
            nextDay = new Date(nextDay.getTime() + oneDay);
            console.log("Checking date ", nextDay);
            if(nextDay.getDay() !== 0 && nextDay.getDay() !== 6) {

                ///not a weekend.
                //TODO check holiday
                console.log("Not a weekend", disabledDates)
                if(!disabledDates.find(h => h.getTime() === nextDay.getTime())) {
                    console.log("Valid day found", nextDay, validDays+1);
                    validDays++;
                }
                else {
                    console.log(disabledDates, "is a holiday")
                }
            }
            else {
                console.log("weekend")
            }
        }
        if(nextDay.getFullYear() !== new Date().getFullYear()) {
            nextDay = new Date(nextDay.getTime() - oneDay);
            --validDays;
        }
        $(this).val(validDays);
        $('#endate').val(`${nextDay.getFullYear()}-${nextDay.getMonth()+1}-${nextDay.getDate()}`);
    } );
 } );