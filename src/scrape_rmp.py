import requests
import json
import pandas as pd
import os
from pathlib import Path
from ratelimit import limits, sleep_and_retry

DATA_DIR = Path("./data").resolve()
CSV_PATH = os.path.join(DATA_DIR, "rmp_ratings.csv")

profs = pd.read_csv("./data/salaries.csv")

profs["name"] = profs["employee"].apply(lambda x: " ".join(x.split(", ")[::-1]))
names = profs["name"].unique()
print(len(names))

# for idx, name in enumerate(names):
#     found = name.find("Wyss")
#     if found != -1:
#         print(idx)
# print(names[4985])

# names = ["Clyde Kruskal"]

# professor name, courses, average rating, reviews (course, rating, date)


def rmp_search(name):
    query = """query NewSearchTeachersQuery(
          $query: TeacherSearchQuery!
      ) {
      newSearch {
          teachers(query: $query) {
          didFallback
          edges {
              cursor
              node {
              id
              legacyId
              firstName
              lastName
              school {
                  name
                  id
              }
              department
              }
          }
          }
      }
  }"""

    variables = {"query": {"text": name}}
    url = "https://www.ratemyprofessors.com/graphql"
    basic = requests.auth.HTTPBasicAuth("test", "test")
    res = requests.post(url, json={"query": query, "variables": variables}, auth=basic)

    data = json.loads(res.text)
    profId = ""

    professors = data["data"]["newSearch"]["teachers"]["edges"]
    if len(professors) > 0:
        for prof in professors:
            if prof["node"]["school"]["id"] == "U2Nob29sLTEyNzA=":
                return prof["node"]["id"]
        return None
    else:
        return None


# @sleep_and_retry
# @limits(calls=2, period=3)
def rmp_get_ratings(name):
    query = """query RatingsListQuery(
	$count: Int!
	$id: ID!
	$courseFilter: String
	$cursor: String
) {
	node(id: $id) {
		__typename
		... on Teacher {
			...RatingsList_teacher_4pguUW
		}
		id
	}
}

fragment RatingsList_teacher_4pguUW on Teacher {
	id
	legacyId
	lastName
	numRatings
	...Rating_teacher
	...NoRatingsArea_teacher
	ratings(first: $count, after: $cursor, courseFilter: $courseFilter) {
		edges {
			cursor
			node {
				...Rating_rating
				id
				__typename
			}
		}
		pageInfo {
			hasNextPage
			endCursor
		}
	}
}

fragment Rating_teacher on Teacher {
	...RatingFooter_teacher
	...RatingSuperHeader_teacher
	...ProfessorNoteSection_teacher
}

fragment NoRatingsArea_teacher on Teacher {
	lastName
	...RateTeacherLink_teacher
}

fragment Rating_rating on Rating {
	comment
	flagStatus
	createdByUser
	teacherNote {
		id
	}
	...RatingHeader_rating
	...RatingSuperHeader_rating
	...RatingValues_rating
	...CourseMeta_rating
	...RatingFooter_rating
	...ProfessorNoteSection_rating
}

fragment RatingHeader_rating on Rating {
	date
	class
	helpfulRating
	clarityRating
# 	isForOnlineClass
}

fragment RatingSuperHeader_rating on Rating {
	legacyId
}

fragment RatingValues_rating on Rating {
	helpfulRating
	clarityRating
	difficultyRating
}

fragment CourseMeta_rating on Rating {
# 	attendanceMandatory
# 	wouldTakeAgain
	grade
# 	textbookUse
# 	isForOnlineClass
# 	isForCredit
}


fragment RatingFooter_rating on Rating {
# 	id
	comment
# 	adminReviewedAt
# 	flagStatus
# 	legacyId
# 	thumbsUpTotal
# 	thumbsDownTotal
	teacherNote {
		id
	}
}

fragment ProfessorNoteSection_rating on Rating {
	teacherNote {
		...ProfessorNote_note
		id
	}
	...ProfessorNoteEditor_rating
}

fragment ProfessorNote_note on TeacherNotes {
	comment
	...ProfessorNoteHeader_note
	...ProfessorNoteFooter_note
}

fragment ProfessorNoteEditor_rating on Rating {
	id
	legacyId
	class
	teacherNote {
		id
		teacherId
		comment
	}
}

fragment ProfessorNoteHeader_note on TeacherNotes {
	createdAt
	updatedAt
}

fragment ProfessorNoteFooter_note on TeacherNotes {
	legacyId
	flagStatus
}

fragment RateTeacherLink_teacher on Teacher {
	legacyId
	numRatings
	lockStatus
}

fragment RatingFooter_teacher on Teacher {
	id
}

fragment RatingSuperHeader_teacher on Teacher {
	firstName
	lastName
	legacyId
	school {
		name
		id
	}
}

fragment ProfessorNoteSection_teacher on Teacher {
	...ProfessorNote_teacher
	...ProfessorNoteEditor_teacher
}

fragment ProfessorNote_teacher on Teacher {
	...ProfessorNoteHeader_teacher
}

fragment ProfessorNoteEditor_teacher on Teacher {
	id
}

fragment ProfessorNoteHeader_teacher on Teacher {
	lastName
}
  """

    id = rmp_search(name)

    if id == None:
        return []

    variablesProbe = {"count": 0, "id": id}
    url = "https://www.ratemyprofessors.com/graphql"
    basic = requests.auth.HTTPBasicAuth("test", "test")
    resProbe = requests.post(
        url, json={"query": query, "variables": variablesProbe}, auth=basic
    )
    data = json.loads(resProbe.text)

    profRatingsCount = 0

    try:
        profRatingsCount = data["data"]["node"]["numRatings"]
    except:
        profRatingsCount = 0

    if profRatingsCount == 0:
        return []

    variables = {"count": profRatingsCount, "id": id}
    res = requests.post(url, json={"query": query, "variables": variables}, auth=basic)
    ratings = json.loads(res.text)["data"]["node"]["ratings"]["edges"]

    return ratings


# out = ""
# splitted = "Justin Olav Wyss-Gallifent".split(" ")
# if len(splitted) == 3:
#     out = splitted[0] + " " + splitted[2]

# print(out)


df = pd.DataFrame(columns=["name", "rating", "courses", "reviews"])

for i, name in enumerate(names):
    splitted = name.split(" ")
    if len(splitted) >= 3:
        name = splitted[0] + " " + splitted[-1]
    print(f"getting reviews for {name} {i}/{len(names)}")
    courses = set()
    ratings = rmp_get_ratings(name)
    reviews = []
    score = 0
    for rating in ratings:
        data = rating["node"]
        course = data["class"]
        courses.add(course)
        score += data["clarityRating"]
        score += data["helpfulRating"]

        reviews.append(
            {
                "professor": name,
                "course": course,
                "review": data["comment"],
                "rating": data["clarityRating"],
                "expected_grade": data["grade"],
                "created": data["date"],
            }
        )

    if len(ratings) != 0:
        score /= len(ratings) * 2
    else:
        score = 0

    df.loc[len(df)] = [name, score, list(courses), reviews]

print("making csv...")
df.to_csv(CSV_PATH, index=False)
