
// 修改光标位置
function changeCursorPosition(node) {
    const selection = window.getSelection()
    // 清除所有选区 如果是 Caret 类型，清除选区后变为 Range，如果不是 Range 类型，后面的 addRange() 就不起作用
    selection.removeAllRanges()
    const range = document.createRange()
    // 选中节点的内容
    range.selectNode(node)
    selection.addRange(range)
    // 取消选中并将光标移至选区最后
    selection.collapseToEnd()
}

// 清除复制后的内容样式
function clearTextStyle(e) {
    e.preventDefault()

    let text
    const clp = (e.originalEvent || e).clipboardData
    if (clp === undefined || clp === null) {
        text = window.clipboardData.getData('text') || ''
        if (text !== '') {
            if (window.getSelection) {
                var newNode = document.createElement('span')
                newNode.innerHTML = text
                window.getSelection().getRangeAt(0).insertNode(newNode)
            } else {
                document.selection.createRange().pasteHTML(text)
            }
        }
    } else {
        text = clp.getData('text/plain') || ''
        if (text !== '') {
            document.execCommand('insertText', false, text)
        }
    }
}

function throttle(delay) {
    let waitForCallFunc
    let canCall = true
    return function helper(callback, ...args) {
        if (!canCall) {
            if (callback) waitForCallFunc = callback
            return
        }

        callback(...args)
        canCall = false
        setTimeout(() => {
            canCall = true
            if (waitForCallFunc) {
                helper(waitForCallFunc, ...args)
                waitForCallFunc = null
            }
        }, delay)
    }
}

function debounce(delay) {
    let timer
    return function(callback, ...args) {
        clearTimeout(timer)
        timer = setTimeout(() => callback.call(null, ...args), delay)
    }
}

/**
 * 计算 dom 到容器顶部的距离
 * @param {HTMLElement} dom 需要计算的容器
 * @param {HTMLElement} topContainer 终止条件
 * @returns 
 */
 function getHeightToTop(dom) {
    let height = dom.offsetTop
    let parent = dom.offsetParent

    while (parent) {
        height += parent.offsetTop
        parent = parent.offsetParent
    }

    return height
}

// dom 是否在屏幕内
function isInScreen(dom) {
    const { top, bottom } = dom.getBoundingClientRect()
    return bottom >= 0 && top < window.innerHeight
}

// dom 在当前屏幕展示内容的百分比
function percentOfdomInScreen(dom) {
    const { height, bottom } = dom.getBoundingClientRect()
    if (bottom <= 0) return 0
    if (bottom >= height) return 1
    return bottom / height
}

function canNodeCalculate(node) {
    return (
        node.innerHTML 
        && node.innerHTML !== '<br>' 
        && !node.textContent.startsWith('```') 
        && isInScreen(node) 
        && percentOfdomInScreen(node) >= 0
    )
}

const editor = document.getElementById("editor");
const showDom = document.getElementById("show-content");
const markdown = new showdown.Converter();
console.log(editor.innerHTML);
showDom.innerHTML = markdown.makeHtml(editor.innerHTML);

function onInput() {
    console.log(1)
    // 为每个元素加上索引，通过索引找到 markdown 渲染后的元素
    let index = 0
    const data = Array.from(editor.children)
    data.forEach(item => {
        delete item.dataset.index
        // 忽略 br 换行符和空文本字节
        if (item.tagName !== 'BR' && item.innerText.trim() !== '') {
            if (!item.children.length || (item.children.length === 1 && item.children[0].tagName === 'BR')) {
                item.dataset.index = index++
                return
            }

            // 这里主要是针对复制过来的有嵌套节点的内容
            const frag = document.createDocumentFragment()
            Array.from(item.childNodes).forEach(e => {
                if (e.nodeType === Node.TEXT_NODE) {
                    const div = document.createElement('div')
                    div.textContent = e.nodeValue
                    item.replaceChild(div, e)
                    div.dataset.index = index++
                    frag.appendChild(div)
                } else if (item.tagName !== 'BR') {
                    e.dataset?.index && delete e.dataset.index
                    e.dataset.index = index++
                    frag.appendChild(e)
                }
            })
            
            editor.replaceChild(frag, item)
            
            // 需要修改光标位置，不然光标会在复制内容的前面，修改后会在复制内容的后面
            changeCursorPosition(editor.querySelector(`[data-index="${index - 1}"]`))
        }
    })

    showDom.innerHTML = markdown.makeHtml(editor.childNodes)
}

const debounceFn = debounce(100) // 防抖
editor.oninput = () => {
    debounceFn(onInput)
}

editor.onpaste = (e) => {
    clearTextStyle(e)
}

// 是否允许滚动
const canScroll = {
    editor: true,
    showDom: true,
}

const debounceFn2 = debounce(100) // 防抖
const throttleFn = throttle(50) // 节流
editor.onscroll = () => {
    if (!canScroll.editor) return

    canScroll.showDom = false
    throttleFn(onScroll, editor, showDom)
    debounceFn2(resumeScroll)
}

showDom.onscroll = () => {
    if (!canScroll.showDom) return

    canScroll.editor = false
    throttleFn(onScroll, showDom, editor)
    debounceFn(resumeScroll)
}

// 恢复滚动
function resumeScroll() {
    canScroll.editor = true
    canScroll.showDom = true
}

/**
 * 
 * @param {HTMLElement} scrollContainer 正在滚动的容器
 * @param {HTMLElement} ShowContainer 需要同步滚动的容器
 * @returns 
 */
function onScroll(scrollContainer, ShowContainer) {
    const scrollHeight = ShowContainer.scrollHeight
    // 滚动到底部
    if (scrollContainer.offsetHeight + scrollContainer.scrollTop >= scrollContainer.scrollHeight) {
        ShowContainer.scrollTo({ top: scrollHeight - ShowContainer.clientHeight })
        return
    }

    // 滚动到顶部
    if (scrollContainer.scrollTop === 0) {
        ShowContainer.scrollTo({ top: 0 })
        return
    }

    const nodes = Array.from(scrollContainer.children)
    for (const node of nodes) {
        // 从上往下遍历，找到第一个在屏幕内的元素
        if (canNodeCalculate(node)) {
            // 如果当前滚动的元素是 <pre> <table>
            if (node.tagName === 'PRE' || node.tagName === 'TABLE') {
                // 如果 pre 里面的子元素同步滚动了，则直接返回
                if (hasPreElementInScrollContainerScroll(node, ShowContainer)) return
                // 否则直接从下一个元素开始计算
                continue
            }

            const index = node.dataset.index
            const dom = ShowContainer.querySelector(`[data-index="${index}"]`)
            if (!dom) continue

            const percent = percentOfdomInScreen(node)
            const heightToTop = getHeightToTop(dom)
            const domNeedHideHeight = dom.offsetHeight * (1 - percent)
            ShowContainer.scrollTo({ top: heightToTop + domNeedHideHeight })
            break
        }
    }
}

function hasPreElementInScrollContainerScroll(preElement, ShowContainer) {
    for (const node of preElement.children[0].children) {
        // 从上往下遍历，找到第一个在屏幕内的元素
        if (isInScreen(node) && percentOfdomInScreen(node) >= 0) {
            const index = node.dataset.index
            const dom = ShowContainer.querySelector(`[data-index="${index}"]`)
            if (!dom) continue

            const percent = percentOfdomInScreen(node)
            const heightToTop = getHeightToTop(dom)
            const domNeedHideHeight = dom.offsetHeight * (1 - percent)
            ShowContainer.scrollTo({ top: heightToTop + domNeedHideHeight })
            return true
        }
    }

    return false
}