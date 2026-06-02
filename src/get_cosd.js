async function downloadAllSourcesCountiesAndYears() {
    const sources = ["ed", "hsp", "crs"];

    const counties = [
        "Alameda", "Alpine", "Amador", "Butte", "Calaveras", "Colusa", "Contra Costa", "Del Norte",
        "El Dorado", "Fresno", "Glenn", "Humboldt", "Imperial", "Inyo", "Kern", "Kings", "Lake",
        "Lassen", "Los Angeles", "Madera", "Marin", "Mariposa", "Mendocino", "Merced", "Modoc",
        "Mono", "Monterey", "Napa", "Nevada", "Orange", "Placer", "Plumas", "Riverside", "Sacramento",
        "San Benito", "San Bernardino", "San Diego", "San Francisco", "San Joaquin", "San Luis Obispo",
        "San Mateo", "Santa Barbara", "Santa Clara", "Santa Cruz", "Shasta", "Sierra", "Siskiyou",
        "Solano", "Sonoma", "Stanislaus", "Sutter", "Tehama", "Trinity", "Tulare", "Tuolumne",
        "Ventura", "Yolo", "Yuba"
    ];

    const years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024];

    console.log(`Started.`);

    for (let s = 0; s < sources.length; s++) {
        let sourceVal = sources[s];
        console.log(`Data Source: ${sourceVal}`);

        $("input[name='CTY-src_m'][value='" + sourceVal + "']").prop("checked", true).trigger("change");

        await new Promise(resolve => setTimeout(resolve, 5000));

        for (let i = 0; i < counties.length; i++) {
            let countyName = counties[i];
            console.log(`County: ${countyName}`);

            let selectizeElement = $("#county2")[0];
            let selectizeDropdown = selectizeElement ? selectizeElement.selectize : null;

            if (selectizeDropdown) {
                selectizeDropdown.setValue(countyName);
            } else {
                $("#county2").val(countyName).trigger("change");
            }

            await new Promise(resolve => setTimeout(resolve, 3000));

            for (let j = 0; j < years.length; j++) {
                let year = years[j];
                console.log(`Year: ${year}`);

                let slider = $("#CTY-year_m").data("ionRangeSlider");

                if (slider) {
                    slider.update({from: year});
                    $("#CTY-year_m").trigger("change");
                } else {
                    $("#CTY-year_m").val(year).trigger("change");
                }

                await new Promise(resolve => setTimeout(resolve, 6000));

                document.getElementById("CTY-dlMap").click();

                await new Promise(resolve => setTimeout(resolve, 3000));
            }
        }
    }

    console.log("Finished.");
}

downloadAllSourcesCountiesAndYears();