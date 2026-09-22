import React from "react";
import PropTypes from "prop-types";
import { useEffect, useRef } from "react";

/**
 * Renders a list of items and automatically scrolls the item at `activeIndex`
 * into the center of the viewport whenever the active index changes.
 *
 * @param {Array} props.list items to render
 * @param {number} props.activeIndex index of the item to scroll into view
 * @param {function(*, number): React.ReactNode} props.renderItem
 *        called for each item to produce its rendered content, receives the
 *        item and its index.
 */
function AutoScrollList(props) {
  const elementRefs = useRef([]);

  useEffect(() => {
    if (
      props.activeIndex !== undefined &&
      props.activeIndex >= 0 &&
      elementRefs.current[props.activeIndex]
    ) {
      elementRefs.current[props.activeIndex]?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }
  }, [props.activeIndex]);

  return (
    <>
      {props.list.map((element, index) => {
        return (
          <div
            key={`scroll-item-${index}`}
            style={{ width: "100%" }}
            ref={(el) => {
              elementRefs.current[index] = el;
            }}
          >
            {props.renderItem(element, index)}
          </div>
        );
      })}
    </>
  );
}

AutoScrollList.propTypes = {
  /** Items to render. */
  list: PropTypes.array.isRequired,
  /** Index of the item to scroll into view. */
  activeIndex: PropTypes.number,
  /** Called for each item to produce its rendered content. */
  renderItem: PropTypes.func.isRequired,
};

export default AutoScrollList;
