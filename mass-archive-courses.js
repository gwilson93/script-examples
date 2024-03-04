/**
 * Retrieve and read a file selected by the user
 * from their local file system.
 * 
 * For the Mass Archive Courses tool, use the following file format:
 *      360LEARNING_CONTAINER_URL
 *      course_id,course_name
 *      ...
 * Example:
 *      tech-services@360learning.com
 *      64947a463bdcc3fb5097ede7,Test Course
 *      64947b52e3f91b85eae789a7,Hello World
 */
async function getFile() {
    // Prompt user to provide local file
    let input = document.createElement('input');
    input.type = 'file';

    // Add an event listener to handle file selection
    return new Promise(function(resolve, reject) {
        input.addEventListener('change', function(event) {
            let file = event.target.files[0];
            let reader = new FileReader();
    
            // Read the file contents
            reader.onload = function(event) {
                var contents = event.target.result;
                resolve(contents);
            };
            reader.readAsText(file);
        });
    
        // Trigger a click event on the input element to open the file picker
        input.click();
    })
}

/**
 * Uses the 360Learning internal API to archive the given course from the platform
 * @param {string} courseId - the 360Learning course ID
 * @param {*} baseURL - the URL of the 360Learning container/platform.
 *                      Example: app.360learning.com
 */
async function archiveCourse(courseId, baseURL) {
    url = 'https://'+baseURL+'/api/courses/archive/'+courseId
    // console.log(url)
    await fetch(url, {
        "headers": {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en-GB;q=0.9,en;q=0.8,es-US;q=0.7,es;q=0.6",
            "content-type": "application/json;charset=UTF-8",
            "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-requested-with": "XMLHttpRequest"
        },
        "referrer": "https://tech-services.360learning.com/home/stats/courses/mine/active",
        "referrerPolicy": "strict-origin-when-cross-origin",
        "body": "{}",
        "method": "PUT",
        "mode": "cors",
        "credentials": "include"
    })
    .then(response => {
        if(response.ok) {
            return response.json();
        } else {
            throw Error(response.status + ": " + response.statusText)
        }
    })
    .catch(error => {
        console.error(error);
    })
}

async function createCourse(apiUrl, name) {
    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name }),
      });
  
      const data = await response.json();
      console.log('Response:', data);
    } catch (error) {
      console.error('Error:', error);
    }
  }
  
  // Function to read CSV file and process each name
  function processCSV(apiUrl, csvData) {
    const lines = csvData.split('\n');
    lines.forEach((line) => {
      const name = line.trim(); // Assuming each line contains a name
      if (name) {
        createCourse(apiUrl, name);
      }
    });
  }

async function main() {
    var text = await getFile();
    text = text.split('\n');
    // First row should be the base URL of the platform
    const baseURL = text[0];
    // The remaining rows follow this syntax: course_ID,course_name
    const courses = text.slice(1);

    for(const course of courses) {
        // Extract the course ID
        const id = course.substring(0, course.indexOf(','));
        try {
            await archiveCourse(id, baseURL);
        } catch(error) {
            console.error(error);
        }
    }
}

main();