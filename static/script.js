// ==========================================
// CURRENT SEARCH LEADS
// ==========================================

window.allLeads = [];


// ==========================================
// SEARCH FORM
// ==========================================

const searchForm =
    document.getElementById("searchForm");

if (searchForm) {

    searchForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const keyword =
                document
                    .getElementById("keyword")
                    .value
                    .trim();


            const city =
                document
                    .getElementById("city")
                    .value
                    .trim();


            if (!keyword || !city) {

                alert(
                    "Please enter keyword and city."
                );

                return;
            }


            const button =
                document.getElementById(
                    "searchButton"
                );


            button.innerText =
                "Searching...";


            button.disabled =
                true;


            // Clear previous screen
            window.allLeads = [];

            updateStats([]);

            updateCategoryFilter([]);

            displayLeads([]);


            try {

                const response =
                    await fetch(
                        "/search",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({
                                keyword: keyword,
                                city: city
                            })
                        }
                    );


                const data =
                    await response.json();


                console.log(
                    "Search API Response:",
                    data
                );


                if (
                    data.success &&
                    data.leads &&
                    data.leads.length > 0
                ) {

                    // ONLY CURRENT SEARCH
                    window.allLeads =
                        data.leads;


                    updateStats(
                        window.allLeads
                    );


                    updateCategoryFilter(
                        window.allLeads
                    );


                    displayLeads(
                        window.allLeads
                    );


                    const results =
                        document.getElementById(
                            "results"
                        );


                    if (results) {

                        results.style.display =
                            "block";

                    }


                } else {

                    window.allLeads = [];

                    updateStats([]);

                    updateCategoryFilter([]);

                    displayLeads([]);


                    const results =
                        document.getElementById(
                            "results"
                        );


                    if (results) {

                        results.style.display =
                            "block";

                    }


                    alert(
                        data.message ||
                        "No businesses found. "
                        +
                        "Please try another keyword or city."
                    );
                }


            } catch (error) {

                console.error(
                    "Search error:",
                    error
                );


                window.allLeads = [];

                updateStats([]);

                updateCategoryFilter([]);

                displayLeads([]);


                alert(
                    "Something went wrong while searching."
                );


            } finally {

                button.innerText =
                    "🔍 Search Leads";


                button.disabled =
                    false;

            }

        }
    );

}


// ==========================================
// UPDATE KPI STATS
// ==========================================

function updateStats(
    leads
) {

    const totalLeads =
        leads.length;


    const websites =
        leads.filter(
            lead => lead.website
        ).length;


    const emails =
        leads.filter(
            lead => lead.email
        ).length;


    const socialProfiles =
        leads.filter(
            lead =>
                lead.instagram ||
                lead.facebook ||
                lead.linkedin ||
                lead.twitter
        ).length;


    const totalLeadsElement =
        document.getElementById(
            "totalLeads"
        );


    const totalWebsitesElement =
        document.getElementById(
            "totalWebsites"
        );


    const totalEmailsElement =
        document.getElementById(
            "totalEmails"
        );


    const totalSocialElement =
        document.getElementById(
            "totalSocial"
        );


    if (totalLeadsElement) {

        totalLeadsElement.innerText =
            totalLeads;

    }


    if (totalWebsitesElement) {

        totalWebsitesElement.innerText =
            websites;

    }


    if (totalEmailsElement) {

        totalEmailsElement.innerText =
            emails;

    }


    if (totalSocialElement) {

        totalSocialElement.innerText =
            socialProfiles;

    }

}


// ==========================================
// UPDATE CATEGORY FILTER
// ==========================================

function updateCategoryFilter(
    leads
) {

    const categoryFilter =
        document.getElementById(
            "categoryFilter"
        );


    if (!categoryFilter) {
        return;
    }


    categoryFilter.innerHTML =
        '<option value="">All Categories</option>';


    const categories = [

        ...new Set(

            leads

                .map(
                    lead => lead.category
                )

                .filter(
                    category => category
                )

        )

    ];


    categories.forEach(
        function (category) {

            const option =
                document.createElement(
                    "option"
                );


            option.value =
                category;


            option.textContent =
                category
                    .charAt(0)
                    .toUpperCase()
                +
                category.slice(1);


            categoryFilter.appendChild(
                option
            );

        }
    );

}


// ==========================================
// DISPLAY LEADS
// ==========================================

function displayLeads(
    leads
) {

    const tableBody =
        document.getElementById(
            "leadTableBody"
        );


    if (!tableBody) {
        return;
    }


    tableBody.innerHTML = "";


    const leadCount =
        document.getElementById(
            "leadCount"
        );


    if (leadCount) {

        leadCount.innerText =
            leads.length + " Leads";

    }


    if (leads.length === 0) {

        const row =
            document.createElement(
                "tr"
            );


        row.innerHTML = `
            <td
                colspan="17"
                style="
                    text-align:center;
                    padding:40px;
                    color:#98a4b5;
                "
            >
                No leads found.
            </td>
        `;


        tableBody.appendChild(
            row
        );


        return;
    }


    leads.forEach(
        function (lead) {

            const row =
                document.createElement(
                    "tr"
                );


            // ==================================
            // RELIABILITY
            // ==================================

            let reliabilityHTML =
                "-";


            if (
                lead.reliability_score !==
                    undefined
                &&
                lead.reliability_score !==
                    null
            ) {

                let badgeClass =
                    "low";


                if (
                    lead.reliability_status ===
                    "HIGH"
                ) {

                    badgeClass =
                        "high";

                }

                else if (
                    lead.reliability_status ===
                    "MEDIUM"
                ) {

                    badgeClass =
                        "medium";

                }


                reliabilityHTML = `
                    <span
                        class="reliability-badge ${badgeClass}"
                    >

                        <span
                            class="reliability-score"
                        >
                            ${lead.reliability_score}%
                        </span>

                        <span
                            class="reliability-label"
                        >
                            ${
                                lead.reliability_status
                                || ""
                            }
                        </span>

                    </span>
                `;

            }


            // ==================================
            // HIGH RELIABILITY ROW
            // ==================================

            if (
                lead.reliability_status ===
                "HIGH"
            ) {

                row.classList.add(
                    "high-reliability-row"
                );

            }


            // ==================================
            // TABLE ROW
            // ==================================

            row.innerHTML = `

                <!-- BUSINESS -->

                <td>
                    ${
                        lead.business_name
                        || "-"
                    }
                </td>


                <!-- CATEGORY -->

                <td>
                    ${
                        lead.category
                        || "-"
                    }
                </td>


                <!-- ADDRESS -->

                <td>
                    ${
                        lead.address
                        || "-"
                    }
                </td>


                <!-- CITY -->

                <td>
                    ${
                        lead.city
                        || "-"
                    }
                </td>


                <!-- PINCODE -->

                <td>
                    ${
                        lead.pincode
                        || "-"
                    }
                </td>


                <!-- PHONE -->

                <td>
                    ${
                        lead.phone
                        || "-"
                    }
                </td>


                <!-- WEBSITE -->

                <td>

                    ${
                        lead.website

                        ?

                        `<a
                            href="${lead.website}"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            Visit
                        </a>`

                        :

                        "-"
                    }

                </td>


                <!-- EMAIL -->

                <td>
                    ${
                        lead.email
                        || "-"
                    }
                </td>


                <!-- INSTAGRAM -->

                <td>

                    ${
                        lead.instagram

                        ?

                        `<a
                            href="${lead.instagram}"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            Instagram
                        </a>`

                        :

                        "-"
                    }

                </td>


                <!-- FACEBOOK -->

                <td>

                    ${
                        lead.facebook

                        ?

                        `<a
                            href="${lead.facebook}"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            Facebook
                        </a>`

                        :

                        "-"
                    }

                </td>


                <!-- LINKEDIN -->

                <td>

                    ${
                        lead.linkedin

                        ?

                        `<a
                            href="${lead.linkedin}"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            LinkedIn
                        </a>`

                        :

                        "-"
                    }

                </td>


                <!-- TWITTER -->

                <td>

                    ${
                        lead.twitter

                        ?

                        `<a
                            href="${lead.twitter}"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            Twitter/X
                        </a>`

                        :

                        "-"
                    }

                </td>


                <!-- RATING -->

                <td>
                    ${
                        lead.rating
                        || "-"
                    }
                </td>


                <!-- REVIEWS -->

                <td>
                    ${
                        lead.review_count
                        || "-"
                    }
                </td>


                <!-- RELIABILITY -->

                <td>
                    ${reliabilityHTML}
                </td>


                <!-- MISSING INFO -->

                <td>
                    ${
                        lead.missing_information
                        || "None"
                    }
                </td>


                <!-- GOOGLE MAPS -->

                <td>

                    ${
                        lead.maps_search_link

                        ?

                        `<a
                            href="${lead.maps_search_link}"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            View Map
                        </a>`

                        :

                        "-"
                    }

                </td>

            `;


            tableBody.appendChild(
                row
            );

        }
    );


    // ==================================
    // RESET HORIZONTAL SCROLL
    // ==================================

    const tableContainer =
        document.querySelector(
            ".table-container"
        );


    if (tableContainer) {

        tableContainer.scrollLeft =
            0;

    }

}


// ==========================================
// FILTER LEADS
// ==========================================

function filterLeads() {

    const searchInput =
        document.getElementById(
            "leadSearch"
        );


    const categoryInput =
        document.getElementById(
            "categoryFilter"
        );


    if (!searchInput || !categoryInput) {
        return;
    }


    const searchText =
        searchInput.value
            .toLowerCase()
            .trim();


    const category =
        categoryInput.value;


    const allLeads =
        window.allLeads || [];


    const filteredLeads =
        allLeads.filter(
            function (lead) {

                const businessName =
                    (
                        lead.business_name
                        || ""
                    ).toLowerCase();


                const matchesSearch =
                    businessName.includes(
                        searchText
                    );


                const matchesCategory =
                    !category
                    ||
                    lead.category ===
                        category;


                return (
                    matchesSearch
                    &&
                    matchesCategory
                );

            }
        );


    displayLeads(
        filteredLeads
    );

}


// ==========================================
// SEARCH FILTER
// ==========================================

const leadSearch =
    document.getElementById(
        "leadSearch"
    );


if (leadSearch) {

    leadSearch.addEventListener(
        "input",
        filterLeads
    );

}


// ==========================================
// CATEGORY FILTER
// ==========================================

const categoryFilter =
    document.getElementById(
        "categoryFilter"
    );


if (categoryFilter) {

    categoryFilter.addEventListener(
        "change",
        filterLeads
    );

}


// ==========================================
// CLEAR FILTERS
// ==========================================

const clearFilters =
    document.getElementById(
        "clearFilters"
    );


if (clearFilters) {

    clearFilters.addEventListener(
        "click",
        function () {

            if (leadSearch) {

                leadSearch.value =
                    "";

            }


            if (categoryFilter) {

                categoryFilter.value =
                    "";

            }


            displayLeads(
                window.allLeads || []
            );

        }
    );

}


// ==========================================
// EXPORT CSV
// ==========================================

const exportCsv =
    document.getElementById(
        "exportCsv"
    );


if (exportCsv) {

    exportCsv.addEventListener(
        "click",
        async function () {

            const leads =
                window.allLeads || [];


            if (!leads.length) {

                alert(
                    "Please search and generate leads first."
                );

                return;
            }


            const keyword =
                document.getElementById(
                    "keyword"
                ).value.trim();


            const city =
                document.getElementById(
                    "city"
                ).value.trim();


            try {

                const response =
                    await fetch(
                        "/export/csv",
                        {
                            method:
                                "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({

                                    leads:
                                        leads,

                                    keyword:
                                        keyword,

                                    city:
                                        city

                                })
                        }
                    );


                if (!response.ok) {

                    throw new Error(
                        "CSV export failed"
                    );

                }


                const blob =
                    await response.blob();


                const url =
                    window.URL.createObjectURL(
                        blob
                    );


                const link =
                    document.createElement(
                        "a"
                    );


                link.href =
                    url;


                link.download =
                    "b2b_leads.csv";


                document.body.appendChild(
                    link
                );


                link.click();


                link.remove();


                window.URL.revokeObjectURL(
                    url
                );


            } catch (error) {

                console.error(
                    "CSV export error:",
                    error
                );


                alert(
                    "Unable to export CSV."
                );

            }

        }
    );

}


// ==========================================
// EXPORT EXCEL
// ==========================================

const exportExcel =
    document.getElementById(
        "exportExcel"
    );


if (exportExcel) {

    exportExcel.addEventListener(
        "click",
        async function () {

            const leads =
                window.allLeads || [];


            if (!leads.length) {

                alert(
                    "Please search and generate leads first."
                );

                return;
            }


            const keyword =
                document.getElementById(
                    "keyword"
                ).value.trim();


            const city =
                document.getElementById(
                    "city"
                ).value.trim();


            try {

                const response =
                    await fetch(
                        "/export/excel",
                        {
                            method:
                                "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({

                                    leads:
                                        leads,

                                    keyword:
                                        keyword,

                                    city:
                                        city

                                })
                        }
                    );


                if (!response.ok) {

                    throw new Error(
                        "Excel export failed"
                    );

                }


                const blob =
                    await response.blob();


                const url =
                    window.URL.createObjectURL(
                        blob
                    );


                const link =
                    document.createElement(
                        "a"
                    );


                link.href =
                    url;


                link.download =
                    "b2b_leads.xlsx";


                document.body.appendChild(
                    link
                );


                link.click();


                link.remove();


                window.URL.revokeObjectURL(
                    url
                );


            } catch (error) {

                console.error(
                    "Excel export error:",
                    error
                );


                alert(
                    "Unable to export Excel."
                );

            }

        }
    );

}
// ==========================================
// MONITOR BACKGROUND ENRICHMENT
// ==========================================

async function monitorEnrichment(jobId) {

    const poll = async () => {

        try {

            const response = await fetch(
                `/enrichment-status/${jobId}`
            );

            const data = await response.json();

            if (!data.success) {
                return;
            }


            // Update current leads
            if (data.leads) {

                window.allLeads =
                    data.leads;

                updateStats(
                    window.allLeads
                );

                updateCategoryFilter(
                    window.allLeads
                );

                displayLeads(
                    window.allLeads
                );
            }


            // Continue until complete
            if (
                data.status === "queued" ||
                data.status === "running"
            ) {

                setTimeout(
                    poll,
                    1000
                );

            } else {

                console.log(
                    "Enrichment completed:",
                    data.status
                );

            }

        } catch (error) {

            console.error(
                "Enrichment polling error:",
                error
            );

        }
    };


    poll();
}


