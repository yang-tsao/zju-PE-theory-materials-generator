#set page(paper:"a5", columns: 1, flipped: false)
#set text(font: "Microsoft YaHei", lang: "zh", 10pt)
#set page(numbering: "1")
#let data = json("data.json")//.slice(0, 100)
// #data
#let Dfs(i) = {
  type(i)
}
// #data.at(0)
// #Dfs(data.at(0))

#for item in data {
  let node_id = item.at("node_id", default: none)
  let labelled = false
  assert(node_id != none, message: "node_id doesn't exist!")
  let prefix = item.at("prefix", default: none)
  assert(prefix != none, message: "prefix not found!")
  let prob = item.at("prob", default: none)
  if prob != none {
    let question = prob.at("题干", default: none)
    assert(question != none, message: "question doesn't exist!")
    [#question #label(str(node_id))]
    labelled = true
    linebreak()
    let choices = prob.at("选项", default: none)
    if choices != none {
      [#choices.replace("\n", "    ")]
      linebreak()
    }
    let answer = prob.at("答案", default: none)
    if answer != none {
      [*答案：* #answer.replace("\n", "、")]
      linebreak()
    }
    linebreak()
  }
  let sons = item.at("sons", default: none)
  if sons != none {
    if labelled == false {
      [=== #prefix #label(str(node_id))]
      let labelled = true
    } else {
      [=== #prefix]
    }
    // [#item]
    for son in sons {
      [+ #son.at(0) #ref(label(str(son.at(1))), form: "page")]
    }
  }
}


