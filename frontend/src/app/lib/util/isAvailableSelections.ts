import { availableSelectionsType } from "../custom types/availability";

export function isAvailableSelections(availableSelections: availableSelectionsType |{message: string} ):availableSelections is availableSelectionsType {
    return (availableSelections as availableSelectionsType).response !== undefined;
 }