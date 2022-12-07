import requests
import json

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
  basic = requests.auth.HTTPBasicAuth('test', 'test')
  res = requests.post(url, json={"query": query, "variables": variables}, auth=basic)

  data = json.loads(res.text)
  profId = ""

  try:
    profId = data['data']['newSearch']['teachers']['edges'][0]['node']['id']
  except:
    profId = "NA"

  return profId

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
    school {
      id
      legacyId
      name
      city
      state
      avgRating
      numRatings
    }
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
    ...RatingTags_rating
    ...RatingFooter_rating
    ...ProfessorNoteSection_rating
  }

  fragment RatingHeader_rating on Rating {
    date
    class
    helpfulRating
    clarityRating
    isForOnlineClass
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
    attendanceMandatory
    wouldTakeAgain
    grade
    textbookUse
    isForOnlineClass
    isForCredit
  }

  fragment RatingTags_rating on Rating {
    ratingTags
  }

  fragment RatingFooter_rating on Rating {
    id
    comment
    adminReviewedAt
    flagStatus
    legacyId
    thumbsUpTotal
    thumbsDownTotal
    thumbs {
      userId
      thumbsUp
      thumbsDown
      id
    }
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
    legacyId
    lockStatus
    isProfCurrentUser
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
    ...ProfessorNoteFooter_teacher
  }

  fragment ProfessorNoteEditor_teacher on Teacher {
    id
  }

  fragment ProfessorNoteHeader_teacher on Teacher {
    lastName
  }

  fragment ProfessorNoteFooter_teacher on Teacher {
    legacyId
    isProfCurrentUser
  }
  """

  id = rmp_search(name)

  if id == "NA":
    return []

  variablesProbe = {"count":0,"id": id}
  url = "https://www.ratemyprofessors.com/graphql"
  basic = requests.auth.HTTPBasicAuth('test', 'test')
  resProbe = requests.post(url, json={"query": query, "variables": variablesProbe}, auth=basic)
  data = json.loads(resProbe.text)

  profRatingsCount = data['data']['node']['numRatings']

  variables = {"count":profRatingsCount,"id": id}
  res = requests.post(url, json={"query": query, "variables": variables}, auth=basic)
  ratings = json.loads(res.text)['data']['node']['ratings']['edges']

  return ratings

print(rmp_get_ratings("Clyde Kruskal"))