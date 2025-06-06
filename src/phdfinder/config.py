from pathlib import Path

# Get absolute path to the DB inside the data/ folder
DB_PATH = str(Path(__file__).resolve().parents[2] / "data" / "phd_jobs_in_schengen.db")

pages_meta=[{
    "id": "ethz",
    "name": "ETH Zurich - Swiss Federal Institute of Technology",
    "job_vacancies_link": "https://jobs.ethz.ch/",
    "country_code": "CH",
    "country_name": "Switzerland"
  },
  {
    "id": "uio",
    "name": "University of Oslo",
    "job_vacancies_link": "https://www.uio.no/english/about/vacancies/academic/",
    "country_code": "NO",
    "country_name": "Norway"
  },
  {
    "id": "nord",
    "name": "Nord University",
    "job_vacancies_link": "https://www.nord.no/en/about/vacancies",
    "country_code": "NO",
    "country_name": "Norway"
  },
  {
    "id": "ntnu",
    "name": "Norwegian University of Science and Technology (NTNU)",
    "job_vacancies_link": "https://www.ntnu.edu/vacancies",
    "country_code": "NO",
    "country_name": "Norway"
  },
  {
    "id": "uib",
    "name": "University of Bergen",
    "job_vacancies_link": "https://www.uib.no/en/about/84777/vacant-positions-uib",
    "country_code": "NO",
    "country_name": "Norway"
  },
  {
    "id": "nmbu",
    "name": "Norwegian University of Life Sciences (NMBU)",
    "job_vacancies_link": "https://www.nmbu.no/en/about/vacancies",
    "country_code": "NO",
    "country_name": "Norway"
  },
  {
    "id": "unibas",
    "name": "University of Basel",
    "job_vacancies_link": "https://www.unibas.ch/en/Working-at-the-University-of-Basel/Current-Vacancies.html",
    "country_code": "CH",
    "country_name": "Switzerland"
  },
  {
    "id": "uzh",
    "name": "University of Zurich",
    "job_vacancies_link": "https://www.uzh.ch/en/explore/work/jobs.html",
    "country_code": "CH",
    "country_name": "Switzerland"
  },
  {
    "id": "unil",
    "name": "University of Lausanne",
    "job_vacancies_link": "https://www.unil.ch/carrieres/en/home/menuinst/emplois.html",
    "country_code": "CH",
    "country_name": "Switzerland"
  },
  {
    "id": "unibe",
    "name": "University of Bern",
    "job_vacancies_link": "https://www.karriere.unibe.ch/jobs/job_portal/index_eng.html",
    "country_code": "CH",
    "country_name": "Switzerland"
  },
  {
    "id": "uit",
    "name": "University of Tromsø - The Arctic University of Norway",
    "job_vacancies_link": "",
    "country_code": "NO",
    "country_name": "Norway"
  },
  {
    "id": "tum",
    "name": "Technical University of Munich",
    "job_vacancies_link": "",
    "country_code": "DE",
    "country_name": "Germany"
  },
  {
    "id": "dkfz",
    "name": "German Cancer Research Center",
    "job_vacancies_link": "",
    "country_code": "DE",
    "country_name": "Germany"
  },
  {
    "id": "unilu",
    "name": "University of Luxembourg",
    "job_vacancies_link": "",
    "country_code": "LX",
    "country_name": "Luxembourg"

  },
  {
    "id": "kavli_NTNU",
    "name": "Kavli Institute (NTNU)",
    "country_code": "NO",
    "country_name": "Norway",
    "url": "https://www.ntnu.edu/kavli/jobs"
  }
]
