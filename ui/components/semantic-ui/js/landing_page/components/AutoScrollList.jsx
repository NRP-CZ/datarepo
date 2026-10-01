import React from "react";
import PropTypes from "prop-types";
import { useEffect, useRef } from "react";

/**
 * Renders a list of items and automatically scrolls the item at `activeIndex`
 * into the center of the viewport whenever the active index changes.
 *
 * `renderItem` must return a single element whose component forwards its
 * ref to the underlying DOM node (e.g. via React.forwardRef, or a plain
 * DOM element like <div>). AutoScrollList attaches a ref to it directly;
 * it does not wrap items in any extra DOM node.
 *
 * @param {Array} props.items items to render
 * @param {number} props.activeIndex index of the item to scroll into view
 * @param {function(*, number): React.ReactElement} props.renderItem
 */
function AutoScrollList({ items, activeIndex, getKey, renderItem }) {
  const elementRefs = useRef([]);

  useEffect(() => {
    if (
      activeIndex !== undefined &&
      activeIndex >= 0 &&
      elementRefs.current[activeIndex]
    ) {
      elementRefs.current[activeIndex]?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }
  }, [activeIndex]);

  return (
    <>
      {items.map((element, index) => {
        const item = renderItem(element, index);

        return React.cloneElement(item, {
          key: getKey(element, index),
          ref: (el) => {
            elementRefs.current[index] = el;
          },
        });
      })}
    </>
  );
}

AutoScrollList.propTypes = {
  items: PropTypes.array.isRequired,
  activeIndex: PropTypes.number,
  getKey: PropTypes.func.isRequired,
  renderItem: PropTypes.func.isRequired,
};

export default AutoScrollList;