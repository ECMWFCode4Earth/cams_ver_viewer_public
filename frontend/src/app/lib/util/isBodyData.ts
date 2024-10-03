import { bodyDataMenu } from "../custom types/bodydata";

export function isBodyDataMenu(bodyData: bodyDataMenu |{} ):bodyData is bodyDataMenu {
    return (bodyData as bodyDataMenu).observationSource !== undefined;
 }


 export function isBodyDataMenuArray(bodyData: (bodyDataMenu |{})[] ):bodyData is bodyDataMenu[] {
    return (bodyData as bodyDataMenu[])[0].observationSource !== undefined;
 }