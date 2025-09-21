 let buttons = document.querySelectorAll("button");

  buttons.forEach(button => {
    button.classList.add("btn", "btn-primary");
  });


 function loadSubjects(streamID) {
      fetch(`/getSubjects/${streamID}`)
        .then(res => res.json())
        .then(data => {
          let streamSelect = document.getElementById("subject");
          streamSelect.innerHTML = "<option value=''>-- Select Subject --</option>";
          data.forEach(subject => {
            streamSelect.innerHTML += `<option value="${subject.subjectID}">${subject.subjectName}</option>`;
          });
          console.log(streamSelect.value);
        });
    }

    function loadCourses() {
      let semester = document.getElementById("semester").value;
      let subjectID = document.getElementById("subject").value;
      
      fetch(`/getCourses/${subjectID}/${semester}`)
        .then(res => res.json())
        .then(data => {
          let courseSelect = document.getElementById("course");
          courseSelect.innerHTML = "<option value=''>-- Select Course --</option>";
          data.forEach(course => {
            courseSelect.innerHTML += `<option value="${course.courseID}">${course.courseName}</option>`;
          });
        });
    }

    function loadQuestionBanks(courseID) {
      fetch(`/getBanks/${courseID}`)
        .then(res => res.json())
        .then(data => {
          let bankInput = document.getElementById("banks");
          bankInput.innerHTML = "";
          data.forEach(questionBank => {
            bankInput.innerHTML += `<input type="checkbox" name="bankNames" value="${questionBank.questionBankID}"/>${questionBank.questionBankName} ${questionBank.courseID} ${questionBank.questionBankType}`;
          });
          console.log(bankInput.value);
        });
      loadStructure(courseID)
    }
